from PyQt6.QtCore import QObject, pyqtSignal

class CustomerModel(QObject):
    data_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._customers = [
            {"name": "John Doe", "email": "john@example.com", "phone": "555-0101"},
            {"name": "Jane Smith", "email": "jane@example.com", "phone": "555-0102"},
            {"name": "Acme Corp", "email": "contact@acme.com", "phone": "555-0999"}
        ]

    def get_all(self):
        return self._customers

    def add(self, customer):
        self._customers.append(customer)
        self.data_changed.emit()

    def update(self, index, customer):
        if 0 <= index < len(self._customers):
            self._customers[index] = customer
            self.data_changed.emit()

    def delete(self, index):
        if 0 <= index < len(self._customers):
            self._customers.pop(index)
            self.data_changed.emit()

class ProductModel(QObject):
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

class OrderModel(QObject):
    data_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._orders = []

    def get_all(self):
        return self._orders

    def add(self, order):
        # Generate ID if not present
        if 'id' not in order or not order['id']:
            order['id'] = str(len(self._orders) + 1)
        self._orders.append(order)
        self.data_changed.emit()

    def update(self, index, order):
        if 0 <= index < len(self._orders):
            self._orders[index] = order
            self.data_changed.emit()

    def update_by_id(self, order_id, updated_data):
        for i, order in enumerate(self._orders):
            if order.get('id') == order_id:
                self._orders[i].update(updated_data)
                self.data_changed.emit()
                break

    def delete(self, index):
        if 0 <= index < len(self._orders):
            self._orders.pop(index)
            self.data_changed.emit()
