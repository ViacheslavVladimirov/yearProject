from controllers.db_utils import get_connection

class Order:
    def __init__(self):
        self.on_data_changed = []

    def notify(self):
        for callback in self.on_data_changed:
            callback()

    def get_all(self):
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
                # Rename database columns to match application expectations
                order['date'] = str(order['order_date'])
                order['customer'] = order['customer_name']
                order['payment'] = order['payment_method']
                order['total'] = float(order['total_price'])
            
            conn.close()
        return orders

    def add(self, order):
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO orders (order_date, customer_name, payment_method, status, total_price) VALUES (%s, %s, %s, %s, %s)",
                (order['date'], order['customer'], order['payment'], order['status'], order['total'])
            )
            order_id = cursor.lastrowid
            
            for item in order.get('items', []):
                cursor.execute(
                    "INSERT INTO order_items (order_id, product_name, price, amount) VALUES (%s, %s, %s, %s)",
                    (order_id, item['name'], item['price'], item['amount'])
                )
            
            conn.commit()
            conn.close()
            self.notify()

    def update(self, index, order):
        all_orders = self.get_all()
        if 0 <= index < len(all_orders):
            order_id = all_orders[index]['id']
            self.update_by_id(order_id, order)

    def update_by_id(self, order_id, updated_data):
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE orders SET order_date=%s, customer_name=%s, payment_method=%s, status=%s, total_price=%s WHERE id=%s",
                (updated_data['date'], updated_data['customer'], updated_data['payment'], updated_data['status'], updated_data['total'], order_id)
            )
            
            # Update items: easiest way is to delete and re-insert
            cursor.execute("DELETE FROM order_items WHERE order_id = %s", (order_id,))
            for item in updated_data.get('items', []):
                cursor.execute(
                    "INSERT INTO order_items (order_id, product_name, price, amount) VALUES (%s, %s, %s, %s)",
                    (order_id, item['name'], item['price'], item['amount'])
                )
            
            conn.commit()
            conn.close()
            self.notify()

    def delete(self, index):
        all_orders = self.get_all()
        if 0 <= index < len(all_orders):
            order_id = all_orders[index]['id']
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM orders WHERE id=%s", (order_id,))
                conn.commit()
                conn.close()
                self.notify()
