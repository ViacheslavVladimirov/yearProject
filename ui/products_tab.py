from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QHeaderView, 
    QAbstractItemView, QMessageBox, QStackedWidget, 
    QLineEdit, QLabel, QFormLayout
)
from PyQt6.QtCore import Qt

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
    def __init__(self):
        super().__init__()
        self.current_edit_row = -1
        self.setup_ui()
        self.load_sample_data()

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
        self.form_page = ProductForm(on_save=self.on_save, on_cancel=self.on_cancel)

        self.stack.addWidget(self.table_page)
        self.stack.addWidget(self.form_page)

        # Connect signals
        self.products_table.itemSelectionChanged.connect(self.update_buttons_state)
        self.add_prod_btn.clicked.connect(self.on_add)
        self.edit_prod_btn.clicked.connect(self.on_edit)
        self.delete_prod_btn.clicked.connect(self.on_delete)

    def update_buttons_state(self):
        """Enables/disables buttons based on table selection."""
        has_selection = len(self.products_table.selectedItems()) > 0
        self.edit_prod_btn.setEnabled(has_selection)
        self.delete_prod_btn.setEnabled(has_selection)

    def filter_products(self, text):
        """Hides rows that don't match the search text."""
        search_text = text.lower()
        for row in range(self.products_table.rowCount()):
            match = False
            for col in range(self.products_table.columnCount()):
                item = self.products_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.products_table.setRowHidden(row, not match)

    def on_add(self):
        """Switches to form view to add a new product."""
        self.current_edit_row = -1
        self.form_page.clear()
        self.stack.setCurrentWidget(self.form_page)

    def on_edit(self):
        """Switches to form view to edit the selected product."""
        selected_row = self.products_table.currentRow()
        if selected_row >= 0:
            self.current_edit_row = selected_row
            product_data = {
                'name': self.products_table.item(selected_row, 0).text(),
                'price': self.products_table.item(selected_row, 1).text(),
                'stock': self.products_table.item(selected_row, 2).text(),
            }
            self.form_page.set_data(product_data)
            self.stack.setCurrentWidget(self.form_page)

    def on_save(self):
        """Saves product data and returns to table view."""
        data = self.form_page.get_data()
        
        if self.current_edit_row == -1:
            # Adding new
            row = self.products_table.rowCount()
            self.products_table.insertRow(row)
            self.products_table.setItem(row, 0, QTableWidgetItem(data['name']))
            self.products_table.setItem(row, 1, QTableWidgetItem(data['price']))
            self.products_table.setItem(row, 2, QTableWidgetItem(data['stock']))
        else:
            # Editing existing
            row = self.current_edit_row
            self.products_table.setItem(row, 0, QTableWidgetItem(data['name']))
            self.products_table.setItem(row, 1, QTableWidgetItem(data['price']))
            self.products_table.setItem(row, 2, QTableWidgetItem(data['stock']))
        
        self.stack.setCurrentWidget(self.table_page)

    def on_cancel(self):
        """Returns to table view without saving."""
        self.stack.setCurrentWidget(self.table_page)

    def on_delete(self):
        """Removes the selected product from the table."""
        selected_row = self.products_table.currentRow()
        if selected_row >= 0:
            reply = QMessageBox.question(
                self, 'Delete Product',
                'Are you sure you want to delete this product?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.products_table.removeRow(selected_row)

    def get_products(self):
        """Returns a list of product data (name, price)."""
        products = []
        for row in range(self.products_table.rowCount()):
            name = self.products_table.item(row, 0).text()
            price = self.products_table.item(row, 1).text()
            products.append({'name': name, 'price': price})
        return products

    def load_sample_data(self):
        """Populates the table with sample product data."""
        sample_products = [
            ("Laptop", "999.99", "15"),
            ("Mouse", "25.50", "120"),
            ("Keyboard", "45.00", "50"),
            ("Monitor", "199.99", "30"),
            ("USB Cable", "9.99", "200")
        ]

        self.products_table.setRowCount(len(sample_products))
        
        for row, (name, price, stock) in enumerate(sample_products):
            self.products_table.setItem(row, 0, QTableWidgetItem(name))
            self.products_table.setItem(row, 1, QTableWidgetItem(price))
            self.products_table.setItem(row, 2, QTableWidgetItem(stock))
