from PyQt6.QtWidgets import QMessageBox
from .db_utils import get_connection

class ProductController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # Connect view signals to controller actions
        self.view.add_requested.connect(self.on_add_requested)
        self.view.edit_requested.connect(self.on_edit_requested)
        self.view.delete_requested.connect(self.on_delete_requested)
        self.view.save_requested.connect(self.on_save_requested)
        self.view.cancel_requested.connect(self.on_cancel_requested)

        # Initial view update
        self.update_view()

    def get_all_products(self):
        products = []
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()
            conn.close()
        return products

    def update_view(self):
        self.view.display_products(self.get_all_products())

    def on_add_requested(self):
        self.current_edit_index = -1
        self.view.show_form()

    def on_edit_requested(self, index):
        self.current_edit_index = index
        products = self.get_all_products()
        if 0 <= index < len(products):
            product_data = products[index]
            self.view.show_form(product_data)

    def on_delete_requested(self, index):
        reply = QMessageBox.question(
            self.view, 'Delete Product',
            'Are you sure you want to delete this product?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            products = self.get_all_products()
            if 0 <= index < len(products):
                product_id = products[index]['id']
                conn = get_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
                    conn.commit()
                    conn.close()
                    self.update_view()

    def on_save_requested(self, data):
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            if self.current_edit_index == -1:
                cursor.execute(
                    "INSERT INTO products (name, price, stock) VALUES (%s, %s, %s)",
                    (data['name'], data['price'], data['stock'])
                )
            else:
                products = self.get_all_products()
                if 0 <= self.current_edit_index < len(products):
                    product_id = products[self.current_edit_index]['id']
                    cursor.execute(
                        "UPDATE products SET name=%s, price=%s, stock=%s WHERE id=%s",
                        (data['name'], data['price'], data['stock'], product_id)
                    )
            conn.commit()
            conn.close()
            self.update_view()
        self.view.show_table()

    def on_cancel_requested(self):
        self.view.show_table()
