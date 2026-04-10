class Customer:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

class Sale:
    def __init__(self, id, customer_id, isPaid, isDelivered, totalAmount, date, status):
        self.id = id
        self.customer_id = customer_id
        self.isPaid = isPaid
        self.isDelivered = isDelivered
        self.totalAmount = totalAmount
        self.date = date
        self.status = status
        self.items = []

class SaleItem:
    def __init__(self, id, product_id, quantity):
        self.id = id
        self.product_id = product_id
        self.quantity = quantity

class Product:
    def __init__(self, id, name, price, stock):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock

class Payment:
    def __init__(self, id, sale_id, amount):
        self.id = id
        self.sale_id = sale_id
        self.amount = amount