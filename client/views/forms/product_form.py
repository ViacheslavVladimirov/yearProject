from PyQt6.QtWidgets import QWidget, QLineEdit, QHBoxLayout, QPushButton, QFormLayout

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
        self.name_input.setText(str(product_data.get('name', '')))

        price = product_data.get('price')
        self.price_input.setText(str(price) if price is not None else "")

        stock = product_data.get('stock')
        self.stock_input.setText(str(stock) if stock is not None else "")


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
