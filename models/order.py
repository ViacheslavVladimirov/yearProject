from PyQt6.QtCore import QObject, pyqtSignal

class Order(QObject):
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
