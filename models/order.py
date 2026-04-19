class Order:
    def __init__(self, id=None, date="", customer="", payment="", status="", total=0.0, items=None):
        self.id = id
        self.date = date
        self.customer = customer
        self.payment = payment
        self.status = status
        self.total = total
        self.items = items or []
