class Product:
    def __init__(self):
        self._products = []
        self.on_data_changed = []

    def notify(self):
        for callback in self.on_data_changed:
            callback()

    def get_all(self):
        return self._products

    def add(self, product):
        self._products.append(product)
        self.notify()

    def update(self, index, product):
        if 0 <= index < len(self._products):
            self._products[index] = product
            self.notify()

    def delete(self, index):
        if 0 <= index < len(self._products):
            self._products.pop(index)
            self.notify()
