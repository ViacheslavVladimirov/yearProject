from PyQt6.QtCore import QObject, pyqtSignal

class Customer(QObject):
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
