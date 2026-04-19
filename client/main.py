import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMainWindow, QTabWidget

from views.orders_view import OrdersView
from views.products_view import ProductsView
from views.customers_view import CustomersView
from views.overview_view import OverviewView

from controllers.customer_controller import CustomerController
from controllers.product_controller import ProductController
from controllers.order_controller import OrderController
from controllers.overview_controller import OverviewController

from controllers.db_utils import init_db

class OrderEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize database
        init_db()

        # Set window title and geometry
        self.setWindowTitle("Order Editor - MVC Structural Refactor")
        self.setGeometry(100, 100, 1000, 700)

        # Initialize Views
        self.orders_tab = OrdersView()
        self.products_tab = ProductsView()
        self.customers_tab = CustomersView()
        self.overview_tab = OverviewView()

        # Initialize Controllers
        self.customer_controller = CustomerController(self.customers_tab)
        self.product_controller = ProductController(self.products_tab)
        self.order_controller = OrderController(
            self.orders_tab, 
            self.customers_tab, self.products_tab
        )
        self.overview_controller = OverviewController(self.overview_tab)
        
        # Link OrderController to OverviewController since models no longer notify
        self.order_controller.on_orders_changed_callbacks.append(self.overview_controller.update_view)

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
