class Customer:
    def __init__(self):
        self._customers = [
            {"name": "John Doe", "email": "john@example.com", "phone": "555-0101"},
            {"name": "Jane Smith", "email": "jane@example.com", "phone": "555-0102"},
            {"name": "Acme Corp", "email": "contact@acme.com", "phone": "555-0999"}
        ]
        self.on_data_changed = []

    def notify(self):
        for callback in self.on_data_changed:
            callback()

    def get_all(self):
        return self._customers

    def add(self, customer):
        self._customers.append(customer)
        self.notify()

    def update(self, index, customer):
        if 0 <= index < len(self._customers):
            self._customers[index] = customer
            self.notify()

    def delete(self, index):
        if 0 <= index < len(self._customers):
            self._customers.pop(index)
            self.notify()
