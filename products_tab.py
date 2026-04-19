from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QHeaderView, 
    QAbstractItemView, QStackedWidget, 
    QLineEdit, QLabel, QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal

class ProductForm(QWidget):
    def __init__(self, on_save, on_cancel):
        super().__init__()
        self.on_save_callback = on_save
        self.on_cancel_callback = on_cancel
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)

        self.name_input = QLineEdit()
        self.price_input = QLineEdit()
        self.stock_input = QLineEdit()

        layout.addRow("Name:", self.name_input)
        layout.addRow("Price:", self.price_input)
        layout.addRow("Stock:", self.stock_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        
        self.save_btn.clicked.connect(self.on_save_callback)
        self.cancel_btn.clicked.connect(self.on_cancel_callback)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addRow(button_layout)

    def set_data(self, product_data):
        self.name_input.setText(product_data.get('name', ''))
        self.price_input.setText(product_data.get('price', ''))
        self.stock_input.setText(product_data.get('stock', ''))

    def get_data(self):
        return {
            'name': self.name_input.text(),
            'price': self.price_input.text(),
            'stock': self.stock_input.text()
        }

    def clear(self):
        self.name_input.clear()
        self.price_input.clear()
        self.stock_input.clear()

class ProductsTab(QWidget):
    add_requested = pyqtSignal()
    edit_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int)
    save_requested = pyqtSignal(dict)
    cancel_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Creates the products management interface."""
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
        self.search_input.setPlaceholderText("Filter products...")
        self.search_input.textChanged.connect(self.filter_products)
        search_layout.addWidget(self.search_input)
        table_layout.addLayout(search_layout)

        self.products_table = QTableWidget()
        self.products_table.setColumnCount(3)
        self.products_table.setHorizontalHeaderLabels(["Name", "Price", "Stock"])
        self.products_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.products_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.products_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.products_table.verticalHeader().hide()

        button_layout = QHBoxLayout()
        self.add_prod_btn = QPushButton("Add Product")
        self.edit_prod_btn = QPushButton("Edit Product")
        self.delete_prod_btn = QPushButton("Delete Product")
        
        self.edit_prod_btn.setEnabled(False)
        self.delete_prod_btn.setEnabled(False)

        button_layout.addWidget(self.add_prod_btn)
        button_layout.addWidget(self.edit_prod_btn)
        button_layout.addWidget(self.delete_prod_btn)

        table_layout.addWidget(self.products_table)
        table_layout.addLayout(button_layout)
        
        # Page 2: Form View
        self.form_page = ProductForm(
            on_save=lambda: self.save_requested.emit(self.form_page.get_data()), 
            on_cancel=lambda: self.cancel_requested.emit()
        )

        self.stack.addWidget(self.table_page)
        self.stack.addWidget(self.form_page)

        # Connect signals
        self.products_table.itemSelectionChanged.connect(self.update_buttons_state)
        self.add_prod_btn.clicked.connect(self.add_requested.emit)
        self.edit_prod_btn.clicked.connect(self._on_edit_clicked)
        self.delete_prod_btn.clicked.connect(self._on_delete_clicked)

    def _on_edit_clicked(self):
        row = self.products_table.currentRow()
        if row >= 0:
            self.edit_requested.emit(row)

    def _on_delete_clicked(self):
        row = self.products_table.currentRow()
        if row >= 0:
            self.delete_requested.emit(row)

    def update_buttons_state(self):
        has_selection = len(self.products_table.selectedItems()) > 0
        self.edit_prod_btn.setEnabled(has_selection)
        self.delete_prod_btn.setEnabled(has_selection)

    def filter_products(self, text):
        search_text = text.lower()
        for row in range(self.products_table.rowCount()):
            match = False
            for col in range(self.products_table.columnCount()):
                item = self.products_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.products_table.setRowHidden(row, not match)

    def display_products(self, products):
        self.products_table.setRowCount(len(products))
        for row, product in enumerate(products):
            self.products_table.setItem(row, 0, QTableWidgetItem(product['name']))
            self.products_table.setItem(row, 1, QTableWidgetItem(product['price']))
            self.products_table.setItem(row, 2, QTableWidgetItem(product['stock']))
        self.filter_products(self.search_input.text())

    def show_form(self, product_data=None):
        if product_data:
            self.form_page.set_data(product_data)
        else:
            self.form_page.clear()
        self.stack.setCurrentWidget(self.form_page)

    def show_table(self):
        self.stack.setCurrentWidget(self.table_page)
