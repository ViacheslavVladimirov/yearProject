from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QHeaderView, 
    QAbstractItemView, QStackedWidget,
    QLineEdit, QLabel
)
from PyQt6.QtCore import pyqtSignal
from views.forms.customer_form import CustomerForm

class CustomersView(QWidget):
    add_requested = pyqtSignal()
    edit_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int)
    save_requested = pyqtSignal(dict)
    cancel_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Creates the customers management interface."""
        self.main_layout = QVBoxLayout(self)

        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        # Page 1: Table View
        self.table_page = QWidget()
        table_layout = QVBoxLayout(self.table_page)

        # Search Bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter customers...")
        self.search_input.textChanged.connect(self.filter_customers)
        search_layout.addWidget(self.search_input)
        table_layout.addLayout(search_layout)

        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(3)
        self.customers_table.setHorizontalHeaderLabels(["Customer Name", "Email", "Phone Number"])
        
        self.customers_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.customers_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.customers_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        header = self.customers_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        button_layout = QHBoxLayout()
        self.add_cust_btn = QPushButton("Add Customer")
        self.edit_cust_btn = QPushButton("Edit Customer")
        self.delete_cust_btn = QPushButton("Delete Customer")

        self.edit_cust_btn.setEnabled(False)
        self.delete_cust_btn.setEnabled(False)

        button_layout.addWidget(self.add_cust_btn)
        button_layout.addWidget(self.edit_cust_btn)
        button_layout.addWidget(self.delete_cust_btn)

        table_layout.addWidget(self.customers_table)
        table_layout.addLayout(button_layout)

        # Page 2: Form View
        self.form_page = CustomerForm(
            on_save=lambda: self.save_requested.emit(self.form_page.get_data()), 
            on_cancel=lambda: self.cancel_requested.emit()
        )

        self.stack.addWidget(self.table_page)
        self.stack.addWidget(self.form_page)

        # Connect signals
        self.customers_table.itemSelectionChanged.connect(self.update_buttons_state)
        self.add_cust_btn.clicked.connect(self.add_requested.emit)
        self.edit_cust_btn.clicked.connect(self._on_edit_clicked)
        self.delete_cust_btn.clicked.connect(self._on_delete_clicked)

    def _on_edit_clicked(self):
        row = self.customers_table.currentRow()
        if row >= 0:
            self.edit_requested.emit(row)

    def _on_delete_clicked(self):
        row = self.customers_table.currentRow()
        if row >= 0:
            self.delete_requested.emit(row)

    def update_buttons_state(self):
        has_selection = len(self.customers_table.selectedItems()) > 0
        self.edit_cust_btn.setEnabled(has_selection)
        self.delete_cust_btn.setEnabled(has_selection)

    def filter_customers(self, text):
        search_text = text.lower()
        for row in range(self.customers_table.rowCount()):
            match = False
            for col in range(self.customers_table.columnCount()):
                item = self.customers_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.customers_table.setRowHidden(row, not match)

    def display_customers(self, customers):
        self.customers_table.setRowCount(len(customers))
        for row, customer in enumerate(customers):
            self.customers_table.setItem(row, 0, QTableWidgetItem(str(customer.get('name', ''))))
            self.customers_table.setItem(row, 1, QTableWidgetItem(str(customer.get('email', ''))))
            self.customers_table.setItem(row, 2, QTableWidgetItem(str(customer.get('phone', ''))))
        self.filter_customers(self.search_input.text())

    def show_form(self, customer_data=None):
        if customer_data:
            self.form_page.set_data(customer_data)
        else:
            self.form_page.clear()
        self.stack.setCurrentWidget(self.form_page)

    def show_table(self):
        self.stack.setCurrentWidget(self.table_page)
