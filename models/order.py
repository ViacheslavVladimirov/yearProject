class Order:
    def __init__(self, id=None, date="", customer="", payment="", status="", total=0.0, items=None):
        self.id = id
        self.date = date
        self.customer = customer
        self.payment = payment
        self.status = status
        self.total = total
        self.items = items or []

    def serialize(self):
        return {
            "id": self.id,
            "date": self.date,
            "customer": self.customer,
            "payment": self.payment,
            "status": self.status,
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
            status=data.get("status", ""),
            total=data.get("total", 0.0),
            items=data.get("items", [])
        )
