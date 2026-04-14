from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QHeaderView, 
    QAbstractItemView, QMessageBox, QStackedWidget,
    QLineEdit, QLabel, QFormLayout
)
from PyQt6.QtCore import Qt

class CustomerForm(QWidget):
    def __init__(self, on_save, on_cancel):
        super().__init__()
        self.on_save_callback = on_save
        self.on_cancel_callback = on_cancel
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)

        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.phone_input = QLineEdit()

        layout.addRow("Customer Name:", self.name_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("Phone Number:", self.phone_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        
        self.save_btn.clicked.connect(self.on_save_callback)
        self.cancel_btn.clicked.connect(self.on_cancel_callback)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addRow(button_layout)

    def set_data(self, customer_data):
        self.name_input.setText(customer_data.get('name', ''))
        self.email_input.setText(customer_data.get('email', ''))
        self.phone_input.setText(customer_data.get('phone', ''))

    def get_data(self):
        return {
            'name': self.name_input.text(),
            'email': self.email_input.text(),
            'phone': self.phone_input.text()
        }

    def clear(self):
        self.name_input.clear()
        self.email_input.clear()
        self.phone_input.clear()

class CustomersTab(QWidget):
    def __init__(self):
        super().__init__()
        self.current_edit_row = -1
        self.setup_ui()
        self.load_sample_data()

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
        
        # Configure selection behavior
        self.customers_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.customers_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.customers_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # Make columns stretch to fill the width
        header = self.customers_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Buttons Layout
        button_layout = QHBoxLayout()
        self.add_cust_btn = QPushButton("Add Customer")
        self.edit_cust_btn = QPushButton("Edit Customer")
        self.delete_cust_btn = QPushButton("Delete Customer")

        # Initially disable edit/delete
        self.edit_cust_btn.setEnabled(False)
        self.delete_cust_btn.setEnabled(False)

        button_layout.addWidget(self.add_cust_btn)
        button_layout.addWidget(self.edit_cust_btn)
        button_layout.addWidget(self.delete_cust_btn)

        table_layout.addWidget(self.customers_table)
        table_layout.addLayout(button_layout)

        # Page 2: Form View
        self.form_page = CustomerForm(on_save=self.on_save, on_cancel=self.on_cancel)

        self.stack.addWidget(self.table_page)
        self.stack.addWidget(self.form_page)

        # Connect signals
        self.customers_table.itemSelectionChanged.connect(self.update_buttons_state)
        self.add_cust_btn.clicked.connect(self.on_add)
        self.edit_cust_btn.clicked.connect(self.on_edit)
        self.delete_cust_btn.clicked.connect(self.on_delete)

    def update_buttons_state(self):
        """Enables/disables buttons based on table selection."""
        has_selection = len(self.customers_table.selectedItems()) > 0
        self.edit_cust_btn.setEnabled(has_selection)
        self.delete_cust_btn.setEnabled(has_selection)

    def filter_customers(self, text):
        """Hides rows that don't match the search text."""
        search_text = text.lower()
        for row in range(self.customers_table.rowCount()):
            match = False
            for col in range(self.customers_table.columnCount()):
                item = self.customers_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.customers_table.setRowHidden(row, not match)

    def on_add(self):
        """Switches to form view to add a new customer."""
        self.current_edit_row = -1
        self.form_page.clear()
        self.stack.setCurrentWidget(self.form_page)

    def on_edit(self):
        """Switches to form view to edit the selected customer."""
        selected_row = self.customers_table.currentRow()
        if selected_row >= 0:
            self.current_edit_row = selected_row
            customer_data = {
                'name': self.customers_table.item(selected_row, 0).text(),
                'email': self.customers_table.item(selected_row, 1).text(),
                'phone': self.customers_table.item(selected_row, 2).text()
            }
            self.form_page.set_data(customer_data)
            self.stack.setCurrentWidget(self.form_page)

    def on_save(self):
        """Saves customer data and returns to table view."""
        data = self.form_page.get_data()
        
        if self.current_edit_row == -1:
            # Adding new
            row = self.customers_table.rowCount()
            self.customers_table.insertRow(row)
            self.customers_table.setItem(row, 0, QTableWidgetItem(data['name']))
            self.customers_table.setItem(row, 1, QTableWidgetItem(data['email']))
            self.customers_table.setItem(row, 2, QTableWidgetItem(data['phone']))
        else:
            # Editing existing
            row = self.current_edit_row
            self.customers_table.setItem(row, 0, QTableWidgetItem(data['name']))
            self.customers_table.setItem(row, 1, QTableWidgetItem(data['email']))
            self.customers_table.setItem(row, 2, QTableWidgetItem(data['phone']))
        
        self.stack.setCurrentWidget(self.table_page)

    def on_cancel(self):
        """Returns to table view without saving."""
        self.stack.setCurrentWidget(self.table_page)

    def on_delete(self):
        """Removes the selected customer from the table."""
        selected_row = self.customers_table.currentRow()
        if selected_row >= 0:
            reply = QMessageBox.question(
                self, 'Delete Customer',
                'Are you sure you want to delete this customer?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.customers_table.removeRow(selected_row)

    def get_customers(self):
        """Returns a list of customer names."""
        customers = []
        for row in range(self.customers_table.rowCount()):
            item = self.customers_table.item(row, 0)
            if item:
                customers.append(item.text())
        return customers

    def load_sample_data(self):
        """Populates the table with sample customer data."""
        sample_customers = [
            ("John Doe", "john@example.com", "555-0101"),
            ("Jane Smith", "jane@example.com", "555-0102"),
            ("Acme Corp", "contact@acme.com", "555-0999")
        ]
        self.customers_table.setRowCount(len(sample_customers))
        for row, (name, email, phone) in enumerate(sample_customers):
            self.customers_table.setItem(row, 0, QTableWidgetItem(name))
            self.customers_table.setItem(row, 1, QTableWidgetItem(email))
            self.customers_table.setItem(row, 2, QTableWidgetItem(phone))
