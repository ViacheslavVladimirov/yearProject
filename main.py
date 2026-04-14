import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMainWindow, QTabWidget

from orders_tab import OrdersTab
from products_tab import ProductsTab
from customers_tab import CustomersTab
from overview_tab import OverviewTab

class OrderEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title and geometry
        self.setWindowTitle("Order Editor")
        self.setGeometry(100, 100, 1000, 700)

        # Create tabs first so they can reference each other
        self.customers_tab = CustomersTab()
        self.products_tab = ProductsTab()
        # Pass callbacks to get customers and products
        self.orders_tab = OrdersTab(
            get_customers_callback=self.customers_tab.get_customers,
            get_products_callback=self.products_tab.get_products
        )
        # Create overview tab with callback to get orders
        self.overview_tab = OverviewTab(get_orders_callback=self.orders_tab.get_orders)

        # Create a central widget and a layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create Tab Widget
        self.tabs = QTabWidget()

        # Add Tabs
        self.tabs.addTab(self.orders_tab, "Orders")
        self.tabs.addTab(self.products_tab, "Products")
        self.tabs.addTab(self.customers_tab, "Customers")
        self.tabs.addTab(self.overview_tab, "Overview")

        # Add tabs to layout
        layout.addWidget(self.tabs)
        
        # Refresh overview when tab is changed to it
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        """Refreshes the overview tab if it's the current tab."""
        if self.tabs.widget(index) == self.overview_tab:
            self.overview_tab.refresh()

def main():
    # Create the application object
    app = QApplication(sys.argv)

    # Create and show the main window
    window = OrderEditorWindow()
    window.show()

    # Execute the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
