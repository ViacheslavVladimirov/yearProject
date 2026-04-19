from .db_utils import get_connection

class OrderController:
    def __init__(self, view, customer_view, product_view):
        self.view = view
        self.customer_view = customer_view
        self.product_view = product_view
        
        # We need a way to notify overview, since model notifications are gone.
        # In this refactor, we can either pass the overview controller or use a callback.
        self.on_orders_changed_callbacks = []

        self.view.add_requested.connect(self.on_add_requested)
        self.view.view_requested.connect(self.on_view_requested)
        self.view.save_requested.connect(self.on_save_requested)
        self.view.cancel_requested.connect(self.on_cancel_requested)
        self.view.collect_requested.connect(self.on_collect_requested)

        self.update_view()

    def get_all_orders(self):
        orders = []
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM orders")
            orders = cursor.fetchall()
            
            # Fetch items for each order
            for order in orders:
                cursor.execute("SELECT product_name as name, price, amount FROM order_items WHERE order_id = %s", (order['id'],))
                order['items'] = cursor.fetchall()
                # Mapping for UI
                order['date'] = str(order['order_date'])
                order['customer'] = order['customer_name']
                order['payment'] = order['payment_method']
                order['total'] = float(order['total_price'])
            
            conn.close()
        return orders

    def update_view(self):
        self.view.display_orders(self.get_all_orders())
        for callback in self.on_orders_changed_callbacks:
            callback()

    def on_add_requested(self):
        self.current_edit_index = -1
        # Need to fetch customers and products from DB/Models (Models are now just containers, 
        # so we fetch from DB via local logic or helper)
        customers = self.get_all_customers_names()
        products = self.get_all_products()
        self.view.show_form(None, customers, products)

    def get_all_customers_names(self):
        names = []
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM customers")
            names = [row[0] for row in cursor.fetchall()]
            conn.close()
        return names

    def get_all_products(self):
        products = []
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()
            conn.close()
        return products

    def on_view_requested(self, index):
        self.current_edit_index = index
        orders = self.get_all_orders()
        if 0 <= index < len(orders):
            order_data = orders[index]
            customers = self.get_all_customers_names()
            products = self.get_all_products()
            self.view.show_view_mode(order_data, customers, products)

    def on_save_requested(self, data):
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            if self.current_edit_index == -1:
                cursor.execute(
                    "INSERT INTO orders (order_date, customer_name, payment_method, status, total_price) VALUES (%s, %s, %s, %s, %s)",
                    (data['date'], data['customer'], data['payment'], data['status'], data['total'])
                )
                order_id = cursor.lastrowid
                for item in data.get('items', []):
                    cursor.execute(
                        "INSERT INTO order_items (order_id, product_name, price, amount) VALUES (%s, %s, %s, %s)",
                        (order_id, item['name'], item['price'], item['amount'])
                    )
            else:
                orders = self.get_all_orders()
                if 0 <= self.current_edit_index < len(orders):
                    order_id = orders[self.current_edit_index]['id']
                    cursor.execute(
                        "UPDATE orders SET order_date=%s, customer_name=%s, payment_method=%s, status=%s, total_price=%s WHERE id=%s",
                        (data['date'], data['customer'], data['payment'], data['status'], data['total'], order_id)
                    )
                    cursor.execute("DELETE FROM order_items WHERE order_id = %s", (order_id,))
                    for item in data.get('items', []):
                        cursor.execute(
                            "INSERT INTO order_items (order_id, product_name, price, amount) VALUES (%s, %s, %s, %s)",
                            (order_id, item['name'], item['price'], item['amount'])
                        )
            conn.commit()
            conn.close()
            self.update_view()
        self.view.show_table()

    def on_cancel_requested(self):
        self.view.show_table()

    def on_collect_requested(self):
        if self.current_edit_index >= 0:
            orders = self.get_all_orders()
            if self.current_edit_index < len(orders):
                order_data = orders[self.current_edit_index]
                current_payment = order_data.get('payment', 'None')
                
                if current_payment == "None":
                    payment = self.view.show_payment_dialog(current_payment)
                    if payment:
                        current_payment = payment
                    else:
                        return

                order_data['payment'] = current_payment
                order_data['status'] = "Yes"
                
                # Update in DB
                conn = get_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE orders SET payment_method=%s, status=%s WHERE id=%s",
                        (order_data['payment'], order_data['status'], order_data['id'])
                    )
                    conn.commit()
                    conn.close()
                    self.update_view()
                
                # Re-show in view mode to refresh
                customers = self.get_all_customers_names()
                products = self.get_all_products()
                self.view.show_view_mode(order_data, customers, products)
