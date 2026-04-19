from PyQt6.QtCore import QObject, pyqtSignal

class Product(QObject):
    data_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._products = [
            {"name": "Laptop", "price": "999.99", "stock": "15"},
            {"name": "Mouse", "price": "25.50", "stock": "120"},
            {"name": "Keyboard", "price": "45.00", "stock": "50"},
            {"name": "Monitor", "price": "199.99", "stock": "30"},
            {"name": "USB Cable", "price": "9.99", "stock": "200"}
        ]

    def get_all(self):
        return self._products

    def add(self, product):
        self._products.append(product)
        self.data_changed.emit()

    def update(self, index, product):
        if 0 <= index < len(self._products):
            self._products[index] = product
            self.data_changed.emit()

    def delete(self, index):
        if 0 <= index < len(self._products):
            self._products.pop(index)
            self.data_changed.emit()
