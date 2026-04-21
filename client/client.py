import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMainWindow, QTabWidget, QStackedWidget
from PyQt6.QtCore import QTimer

from views.orders_view import OrdersView
from views.products_view import ProductsView
from views.customers_view import CustomersView
from views.overview_view import OverviewView
from views.empty_menu_view import EmptyMenuView

from controllers.customerController import CustomerController
from controllers.productController import ProductController
from controllers.orderController import OrderController
from controllers.overviewController import OverviewController
from controllers.apiClient import ping

class OrderEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set window title and geometry
        self.setWindowTitle("Order Editor - MVC Structural Refactor")
        self.setGeometry(100, 100, 1000, 700)

        # Main Stacked Widget
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # 1. Empty Menu Screen (Index 0)
        self.empty_view = EmptyMenuView()
        self.stacked_widget.addWidget(self.empty_view)

        # 2. Main UI Screen (Index 1)
        self.main_container = QWidget()
        self.main_layout = QVBoxLayout(self.main_container)
        
        # Initialize Views
        self.orders_tab = OrdersView()
        self.products_tab = ProductsView()
        self.customers_tab = CustomersView()
        self.overview_tab = OverviewView()

        # Create Tab Widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self.orders_tab, "Orders")
        self.tabs.addTab(self.products_tab, "Products")
        self.tabs.addTab(self.customers_tab, "Customers")
        self.tabs.addTab(self.overview_tab, "Overview")
        self.main_layout.addWidget(self.tabs)
        
        self.stacked_widget.addWidget(self.main_container)

        # Initialize Controllers
        self.customer_controller = CustomerController(self.customers_tab)
        self.product_controller = ProductController(self.products_tab)
        self.order_controller = OrderController(
            self.orders_tab, 
            self.customers_tab, self.products_tab
        )
        self.overview_controller = OverviewController(self.overview_tab)
        
        # Link OrderController to OverviewController
        self.order_controller.on_orders_changed_callbacks.append(self.overview_controller.update_view)

        self.stacked_widget.setCurrentIndex(0)

        # Connection Check Timer
        self.is_connected = False
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_connection)
        self.check_timer.start(2000) # Check every 2 seconds

    def check_connection(self):
        connected = ping()
        if connected != self.is_connected:
            self.is_connected = connected
            if connected:
                self.stacked_widget.setCurrentIndex(1)
                self.refresh_all_views()
            else:
                self.stacked_widget.setCurrentIndex(0)

    def refresh_all_views(self):
        # Trigger updates on all controllers to fetch fresh data
        self.customer_controller.update_view()
        self.product_controller.update_view()
        self.order_controller.update_view()
        self.overview_controller.update_view()

def main():
    # Create the application object
    app = QApplication(sys.argv)

    # Create and show the main window
    window = OrderEditorWindow()
    window.show()

    # Execute the application
    sys.exit(app.exec())

main()
