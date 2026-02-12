import model
import datetime
import json

class Controller:
    def __init__(self):
        self.customers = []
        self.orders = []
        self.sales = []
        self.products = []
        self.payments = []
        self.saleItems = []

    def generateId(self, objList):
        lastId = 0

        for obj in objList:
            if obj.id > lastId: 
                lastId = obj.id

        id = lastId + 1
        return id

    def createOrder(self, customer_id, isPaid, isDone, orderItem_id, payment_id, totalAmount):
        id = self.generateId(self.orders)
        date = datetime.date.today
        order = model.Order(id, customer_id, isPaid, isDone, orderItem_id, payment_id, totalAmount, date)

        self.orders.append(order)

    def sale(self, saleItem_id, payment_id): #fix the saleItem_id and payment_id
        id = self.generateId(self.sales)
        date = datetime.date.today
        sale = model.Sale(id, saleItem_id, payment_id, date)

        self.sales.append(sale)

    def registerPayment(self):
        id = self.generateId(self.payments)
        payment = model.Payment()

    def registerSaleItem(self, product_id, quantity):
        id = self.generateId(self.saleItems)
        sale_id = self.generateId(self.sales)
        saleItem = model.SaleItem(id, sale_id, product_id, quantity)

        self.saleItems.append(saleItem)