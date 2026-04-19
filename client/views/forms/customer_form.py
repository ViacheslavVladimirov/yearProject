from PyQt6.QtWidgets import QWidget, QLineEdit, QHBoxLayout, QPushButton, QFormLayout
from PyQt6.QtCore import pyqtSignal

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
        self.name_input.setText(str(customer_data.get('name', '')))
        self.email_input.setText(str(customer_data.get('email', '')))
        self.phone_input.setText(str(customer_data.get('phone', '')))

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
