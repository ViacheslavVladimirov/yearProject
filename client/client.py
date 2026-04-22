import sys

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QMainWindow, 
    QTabWidget, QStackedWidget, QPushButton, QLabel
)
from PyQt6.QtCore import QTimer, Qt, QSize

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

        self.setWindowTitle("Kassa applicatie Aroma")
        self.setGeometry(100, 100, 1000, 700)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.empty_view = EmptyMenuView()
        self.stacked_widget.addWidget(self.empty_view)

        self.main_container = QWidget()
        self.main_layout = QVBoxLayout(self.main_container)

        self.orders_tab = OrdersView()
        self.products_tab = ProductsView()
        self.customers_tab = CustomersView()
        self.overview_tab = OverviewView()

        self.tabs = QTabWidget()
        self.tabs.addTab(self.orders_tab, "Orders")
        self.tabs.addTab(self.products_tab, "Products")
        self.tabs.addTab(self.customers_tab, "Customers")
        self.tabs.addTab(self.overview_tab, "Overview")

        self.global_refresh_btn = QPushButton("Refresh All")
        self.global_refresh_btn.clicked.connect(self.refresh_all_views)
        self.tabs.setCornerWidget(self.global_refresh_btn, Qt.Corner.TopRightCorner)
        
        self.main_layout.addWidget(self.tabs)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("padding: 5px; font-weight: bold;")
        self.main_layout.addWidget(self.status_label)
        
        self.stacked_widget.addWidget(self.main_container)

        self.customer_controller = CustomerController(self.customers_tab)
        self.product_controller = ProductController(self.products_tab)
        self.order_controller = OrderController(
            self.orders_tab, 
            self.customers_tab, self.products_tab
        )
        self.overview_controller = OverviewController(self.overview_tab)

        self.customer_controller.status_callback = self.show_status
        self.product_controller.status_callback = self.show_status
        self.order_controller.status_callback = self.show_status

        self.order_controller.on_orders_changed_callbacks.append(self.overview_controller.update_view)

        self.stacked_widget.setCurrentIndex(0)

        self.is_connected = False
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_connection)
        self.check_timer.start(2000)

    def show_status(self, message, is_error=False):
        color = "red" if is_error else "green"
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"padding: 5px; font-weight: bold; color: {color};")

        QTimer.singleShot(5000, lambda: self.status_label.setText(""))

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
        try:
            self.customer_controller.update_view()
            self.product_controller.update_view()
            self.order_controller.update_view()
            self.overview_controller.update_view()
            self.show_status("All data refreshed")
        except Exception as e:
            self.show_status(f"Refresh failed: {str(e)}", True)

def main():
    app = QApplication(sys.argv)

    window = OrderEditorWindow()
    window.show()

    sys.exit(app.exec())

main()
