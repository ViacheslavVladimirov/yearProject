import model
import datetime
import mysql.connector

PRODUCT_SELECT = "SELECT DISTINCT product_name, product_price, product_stock, product_id FROM project.products"
PRODUCT_INSERT = "INSERT INTO project.products (product_name, product_price, product_stock) VALUES (%s, %s, %s)"
PRODUCT_UPDATE = "UPDATE project.products SET product_name = %s, product_price = %s, product_stock = %s WHERE product_id = %s"
PRODUCT_DELETE = "DELETE FROM project.products WHERE product_id = %s"

CUSTOMER_SELECT = "SELECT customer_name, customer_email, customer_id FROM project.customers"
CUSTOMER_INSERT = "INSERT INTO project.customers (customer_name, customer_email) VALUES (%s, %s)"
CUSTOMER_UPDATE = "UPDATE project.customers SET customer_name = %s, customer_email = %s WHERE customer_id = %s"
CUSTOMER_DELETE = "DELETE FROM project.customers WHERE customer_id = %s"

ORDERS_SELECT = "SELECT sales.sale_id, customers.customer_name, sales.isPaid, sales.total, sales.sale_date FROM project.sales JOIN project.customers ON sales.customer_id = customers.customer_id WHERE sale_status='order' AND isDelivered = FALSE"
ORDERLINE_SELECT = "SELECT products.product_name, salelines.quantity FROM project.salelines JOIN project.products ON salelines.product_id = products.product_id WHERE sale_id = %s"
ORDER_INSERT = "INSERT INTO project.sales (customer_id, isPaid, isDelivered, total, sale_date, sale_status) VALUES (%s, %s, False, %s, %s, 'order')"

SALELINE_INSERT = "INSERT INTO project.salelines (sale_id, product_id, quantity) VALUES (%s, %s, %s)"

SALE_INSERT = "INSERT INTO project.sales (customer_id, isPaid, isDelivered, total, sale_date, sale_status) VALUES (%s, True, True, %s, %s, 'sale')"

PAYMENT_INSERT = "INSERT INTO project.payments (sale_id, amount) VALUES (%s, %s)"


class Controller:
    def __init__(self):
        self.selected_customer = None
        self.current_operation = []
        self.isPaid = False
        self.currentOrderId = None
        self.selected_product_row = None

        print("Before DB connect")
        try:
            self.DB = mysql.connector.connect(
                                host="127.0.0.1",
                                user="root",
                                password="password",
                                database="project",
                                connection_timeout=3,
                                use_pure=True)
            self.cursor = self.DB.cursor()
            print("After DB connect")
        except Exception as e:
             print("error: ", e)

    def listProducts(self):
        self.cursor.execute(PRODUCT_SELECT)
        rows = self.cursor.fetchall()

        return rows
    
    def listCustomers(self):
        self.cursor.execute(CUSTOMER_SELECT)
        rows = self.cursor.fetchall()

        return rows
    
    def registerCustomer(self, name, email):
        self.cursor.execute("SELECT customer_name, customer_email FROM project.customers WHERE customer_name = %s OR customer_email = %s", (name, email))

        if self.cursor.fetchone():
            return False
        else:
            try:
                self.cursor.execute(CUSTOMER_INSERT, (name, email))
                self.DB.commit()
                return True
            except Exception as e:
                print("error: ", e)
                return False
            
    def updateCustomer(self, name, email, id):
        try:
            self.cursor.execute(CUSTOMER_UPDATE, (name, email, id))
            self.DB.commit()
            return True
        except Exception as e:
            print("error: ", e)
            return False
        
    def deleteCustomer(self, id):
        try:
            self.cursor.execute(CUSTOMER_DELETE, (id,))
            self.DB.commit()
            return True
        except Exception as e:
            print("error: ", e)
            return False
            
    def set_customer(self, name, email, id):
        self.selected_customer = (name, email, id)

    def clearCustomer(self):
        self.selected_customer = None

    def addToOperation(self, product, quantity):
        self.current_operation.append({"product": product, "quantity": quantity})

    def clearOperation(self):
        self.current_operation = []
        self.isPaid = False

    def listOrders(self):
        self.cursor.execute(ORDERS_SELECT)
        rows = self.cursor.fetchall()

        return rows
    
    def getSaleLines(self, saleId):
        self.cursor.execute(ORDERLINE_SELECT, (saleId,))
        rows = self.cursor.fetchall()

        return rows
    
    def registerOrder(self, customer_id, isPaid, total):
        try:
            date = datetime.datetime.now()

            self.cursor.execute(ORDER_INSERT, (customer_id, isPaid, total, date))
            order_id = self.cursor.lastrowid

            data = [
            (
                order_id,
                item["product"].id,
                item["quantity"]
            )
            for item in self.current_operation
            ]

            self.cursor.executemany(SALELINE_INSERT, data)
            self.DB.commit()

            return True
        except Exception as e:
            print("Error: ",e)
            return False
        
    def getProductId(self, name):
        self.cursor.execute("SELECT product_id FROM project.products WHERE product_name = %s", (name,))
        id = self.cursor.fetchone()[0]

        return id
    
    def registerSale(self, total, customer_id=None):
        try:
            date = datetime.datetime.now()

            self.cursor.execute(SALE_INSERT, (customer_id, total, date))
            sale_id = self.cursor.lastrowid

            payment_success = self.registerPayment(sale_id, total)

            data = [
            (
                sale_id,
                item["product"].id,
                item["quantity"]
            )
            for item in self.current_operation
            ]

            self.cursor.executemany(SALELINE_INSERT, data)
            if payment_success: self.DB.commit()
            else: return False

            return True
        except Exception as e:
            print("Error: ",e)
            return False
        
    def setPaid(self):
        self.isPaid = True
        return True
    
    def updatePaymentStatus(self, sale_id):
        try:
            self.cursor.execute("UPDATE project.sales SET isPaid = True WHERE sale_id = %s", (sale_id,))
            self.DB.commit()
            return True
        except Exception as e:
            print("error: ", e)
            return False
        
    def completeOrder(self, sale_id):
        try:
            self.cursor.execute("UPDATE project.sales SET isDelivered = True WHERE sale_id = %s", (sale_id,))
            self.DB.commit()
            return True
        except Exception as e:
            print("error: ", e)
            return False
        
    def registerPayment(self, sale_id, amount):
        try:
            self.cursor.execute(PAYMENT_INSERT, (sale_id, amount))
            self.DB.commit()
            return True
        except Exception as e:
            print("error: ", e)
            return False
        
    def registerProduct(self, name, price, stock):
        try:
            self.cursor.execute(PRODUCT_INSERT, (name, price, stock))
            self.DB.commit()
            return True
        except Exception as e:
            print("error: ", e)
            return False
        
    def updateProduct(self, name, price, stock):
        try:
            self.cursor.execute(PRODUCT_UPDATE, (name, price, stock, self.selected_product_row.product_id))
            self.DB.commit()
            return True
        except Exception as e:
            print("error: ", e)
            return False
        
    def deleteProduct(self):
        try:
            self.cursor.execute(PRODUCT_DELETE, (self.selected_product_row.product_id,))
            self.DB.commit()
            return True
        except Exception as e:
            print("error: ", e)
            return False