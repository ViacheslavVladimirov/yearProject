from controllers.db_utils import get_connection

class Customer:
    def __init__(self):
        self.on_data_changed = []

    def notify(self):
        for callback in self.on_data_changed:
            callback()

    def get_all(self):
        customers = []
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM customers")
            customers = cursor.fetchall()
            conn.close()
        return customers

    def add(self, customer):
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO customers (name, email, phone) VALUES (%s, %s, %s)",
                (customer['name'], customer['email'], customer['phone'])
            )
            conn.commit()
            conn.close()
            self.notify()

    def update(self, index, customer):
        # In a database-backed model, it's better to update by ID.
        # However, to maintain compatibility with index-based controller:
        all_customers = self.get_all()
        if 0 <= index < len(all_customers):
            customer_id = all_customers[index]['id']
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE customers SET name=%s, email=%s, phone=%s WHERE id=%s",
                    (customer['name'], customer['email'], customer['phone'], customer_id)
                )
                conn.commit()
                conn.close()
                self.notify()

    def delete(self, index):
        all_customers = self.get_all()
        if 0 <= index < len(all_customers):
            customer_id = all_customers[index]['id']
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM customers WHERE id=%s", (customer_id,))
                conn.commit()
                conn.close()
                self.notify()
