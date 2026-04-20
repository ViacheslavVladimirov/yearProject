class Order:
    def __init__(self, id=None, date="", customer="", payment="", is_delivered=False, total=0.0, items=None):
        self.id = id
        self.date = date
        self.customer = customer
        self.payment = payment
        self.is_delivered = is_delivered
        self.total = total
        self.items = items or []

    def serialize(self):
        return {
            "id": self.id,
            "date": self.date,
            "customer": self.customer,
            "payment": self.payment,
            "is_delivered": self.is_delivered,
            "total": self.total,
            "items": self.items
        }

    @staticmethod
    def deserialize(data):
        return Order(
            id=data.get("id"),
            date=data.get("date", ""),
            customer=data.get("customer", ""),
            payment=data.get("payment", ""),
            is_delivered=bool(data.get("is_delivered", False)),
            total=data.get("total", 0.0),
            items=data.get("items", [])
        )
