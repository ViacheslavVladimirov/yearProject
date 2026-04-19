from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QHeaderView, 
    QAbstractItemView, QStackedWidget, QCheckBox
)
from PyQt6.QtCore import pyqtSignal
from views.forms.order_form import OrderForm, PaymentDialog

class OrdersView(QWidget):
    add_requested = pyqtSignal()
    view_requested = pyqtSignal(int)
    save_requested = pyqtSignal(dict)
    cancel_requested = pyqtSignal()
    collect_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Creates the orders management interface."""
        self.main_layout = QVBoxLayout(self)
        
        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        # Page 1: Table View
        self.table_page = QWidget()
        table_layout = QVBoxLayout(self.table_page)

        self.pending_filter_checkbox = QCheckBox("Only pending orders")
        self.pending_filter_checkbox.stateChanged.connect(self.apply_filter)
        table_layout.addWidget(self.pending_filter_checkbox)

        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(6)
        self.orders_table.setHorizontalHeaderLabels(["Order ID", "Date", "Customer", "Payment", "Delivered", "Total Price"])
        self.orders_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.orders_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.orders_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.orders_table.verticalHeader().hide()

        button_layout = QHBoxLayout()
        self.add_order_btn = QPushButton("Add Order")
        self.view_order_btn = QPushButton("View Order")
        self.view_order_btn.setEnabled(False)

        button_layout.addWidget(self.add_order_btn)
        button_layout.addWidget(self.view_order_btn)

        table_layout.addWidget(self.orders_table)
        table_layout.addLayout(button_layout)
        
        # Page 2: Form View
        self.form_page = OrderForm(
            on_save=lambda: self.save_requested.emit(self.form_page.get_data()), 
            on_cancel=lambda: self.cancel_requested.emit(),
            on_collect=lambda: self.collect_requested.emit()
        )

        self.stack.addWidget(self.table_page)
        self.stack.addWidget(self.form_page)

        # Connect signals
        self.orders_table.itemSelectionChanged.connect(self.update_buttons_state)
        self.add_order_btn.clicked.connect(self.add_requested.emit)
        self.view_order_btn.clicked.connect(self._on_view_clicked)

    def _on_view_clicked(self):
        row = self.orders_table.currentRow()
        if row >= 0:
            self.view_requested.emit(row)

    def update_buttons_state(self):
        has_selection = len(self.orders_table.selectedItems()) > 0
        self.view_order_btn.setEnabled(has_selection)

    def display_orders(self, orders):
        self.orders_table.setRowCount(len(orders))
        for row, order in enumerate(orders):
            self.orders_table.setItem(row, 0, QTableWidgetItem(str(order.get('id', ''))))
            self.orders_table.setItem(row, 1, QTableWidgetItem(str(order.get('date', ''))))
            self.orders_table.setItem(row, 2, QTableWidgetItem(str(order.get('customer', ''))))
            self.orders_table.setItem(row, 3, QTableWidgetItem(str(order.get('payment', ''))))
            self.orders_table.setItem(row, 4, QTableWidgetItem(str(order.get('status', ''))))
            total = order.get('total', 0.0)
            self.orders_table.setItem(row, 5, QTableWidgetItem(f"€ {float(total):.2f}"))
        self.apply_filter()

    def show_form(self, order_data, customers, products):
        self.form_page.set_data(order_data, customers, products)
        self.form_page.set_read_only(False)
        self.stack.setCurrentWidget(self.form_page)

    def show_view_mode(self, order_data, customers, products):
        self.form_page.set_data(order_data, customers, products)
        self.form_page.set_read_only(True)
        self.stack.setCurrentWidget(self.form_page)

    def show_table(self):
        self.stack.setCurrentWidget(self.table_page)

    def show_payment_dialog(self, current_payment):
        dialog = PaymentDialog(self, current_payment)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_payment_method()
        return None

    def apply_filter(self):
        only_pending = self.pending_filter_checkbox.isChecked()
        for row in range(self.orders_table.rowCount()):
            item = self.orders_table.item(row, 4)
            if item:
                is_delivered = item.text() == "Yes"
                should_hide = only_pending and is_delivered
                self.orders_table.setRowHidden(row, should_hide)
