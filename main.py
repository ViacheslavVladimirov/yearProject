import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMainWindow, QTabWidget

from orders_tab import OrdersTab
from products_tab import ProductsTab
from customers_tab import CustomersTab
from overview_tab import OverviewTab

from models import CustomerModel, ProductModel, OrderModel
from controllers import CustomerController, ProductController, OrderController, OverviewController

class OrderEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title and geometry
        self.setWindowTitle("Order Editor - MVC Version")
        self.setGeometry(100, 100, 1000, 700)

        # Initialize Models
        self.customer_model = CustomerModel()
        self.product_model = ProductModel()
        self.order_model = OrderModel()

        # Initialize Views
        self.orders_tab = OrdersTab()
        self.products_tab = ProductsTab()
        self.customers_tab = CustomersTab()
        self.overview_tab = OverviewTab()

        # Initialize Controllers
        self.customer_controller = CustomerController(self.customer_model, self.customers_tab)
        self.product_controller = ProductController(self.product_model, self.products_tab)
        self.order_controller = OrderController(
            self.order_model, self.orders_tab, 
            self.customer_model, self.product_model
        )
        self.overview_controller = OverviewController(self.order_model, self.overview_tab)

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
