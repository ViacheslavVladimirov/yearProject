from PyQt6.QtWidgets import QWidget, QLineEdit, QHBoxLayout, QPushButton, QFormLayout, QMessageBox
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
        self.name_input.setMaxLength(255)
        self.email_input = QLineEdit()
        self.email_input.setMaxLength(255)
        self.phone_input = QLineEdit()
        self.phone_input.setMaxLength(50)

        layout.addRow("Customer Name:", self.name_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("Phone Number:", self.phone_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        
        self.save_btn.clicked.connect(self.validate_and_save)
        self.cancel_btn.clicked.connect(self.on_cancel_callback)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addRow(button_layout)

    def validate_and_save(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()

        if not name or not email or not phone:
            QMessageBox.warning(self, "Validation Error", "All fields are required.")
            return

        self.on_save_callback()

    def set_data(self, customer_data):
        self.name_input.setText(str(customer_data.get('name', '')))
        self.email_input.setText(str(customer_data.get('email', '')))
        self.phone_input.setText(str(customer_data.get('phone', '')))

    def get_data(self):
        return {
            'name': self.name_input.text().strip(),
            'email': self.email_input.text().strip(),
            'phone': self.phone_input.text().strip()
        }

    def clear(self):
        self.name_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
