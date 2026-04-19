from controllers.db_utils import get_connection

class Product:
    def __init__(self):
        self.on_data_changed = []

    def notify(self):
        for callback in self.on_data_changed:
            callback()

    def get_all(self):
        products = []
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()
            conn.close()
        return products

    def add(self, product):
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO products (name, price, stock) VALUES (%s, %s, %s)",
                (product['name'], product['price'], product['stock'])
            )
            conn.commit()
            conn.close()
            self.notify()

    def update(self, index, product):
        all_products = self.get_all()
        if 0 <= index < len(all_products):
            product_id = all_products[index]['id']
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE products SET name=%s, price=%s, stock=%s WHERE id=%s",
                    (product['name'], product['price'], product['stock'], product_id)
                )
                conn.commit()
                conn.close()
                self.notify()

    def delete(self, index):
        all_products = self.get_all()
        if 0 <= index < len(all_products):
            product_id = all_products[index]['id']
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
                conn.commit()
                conn.close()
                self.notify()
