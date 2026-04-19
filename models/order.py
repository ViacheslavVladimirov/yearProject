class Order:
    def __init__(self):
        self._orders = []
        self.on_data_changed = []

    def notify(self):
        for callback in self.on_data_changed:
            callback()

    def get_all(self):
        return self._orders

    def add(self, order):
        # Generate ID if not present
        if 'id' not in order or not order['id']:
            order['id'] = str(len(self._orders) + 1)
        self._orders.append(order)
        self.notify()

    def update(self, index, order):
        if 0 <= index < len(self._orders):
            self._orders[index] = order
            self.notify()

    def update_by_id(self, order_id, updated_data):
        for i, order in enumerate(self._orders):
            if order.get('id') == order_id:
                self._orders[i].update(updated_data)
                self.notify()
                break

    def delete(self, index):
        if 0 <= index < len(self._orders):
            self._orders.pop(index)
            self.notify()
