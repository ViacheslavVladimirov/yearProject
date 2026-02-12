class Customer:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

class Order:
    def __init__(self, id, customer_id, isPaid, isDone, orderItem_id, payment_id, totalAmount, date):
        self.id = id
        self.customer_id = customer_id
        self.isPaid = isPaid
        self.isDone = isDone
        self.orderItem_id = orderItem_id
        self.payment_id = payment_id
        self.totalAmount = totalAmount
        self.date = date

class OrderItem:
    def __init__(self, id, order_id, product_id, quantity):
        self.id = id
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity

class SaleItem:
    def __init__(self, id, sale_id, product_id, quantity):
        self.id = id
        self.sale_id = sale_id
        self.product_id = product_id
        self.quantity = quantity

class Sale:
    def __init__(self, id, saleItem_id, payment_id, date):
        self.id = id
        self.SaleItem_id = saleItem_id
        self.payment_id = payment_id
        self.date = date

class Product:
    def __init__(self, id, name, price, stock):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock

class Payment:
    def __init__(self, id, sale_id, order_id, amount):
        self.id = id
        self.sale_id = sale_id
        self.order_id = order_id
        self.amount = amount