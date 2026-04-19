from PyQt6.QtWidgets import QMessageBox
from .db_utils import get_connection

class CustomerController:
    def __init__(self, view):
        self.view = view

        # Connect view signals to controller actions
        self.view.add_requested.connect(self.on_add_requested)
        self.view.edit_requested.connect(self.on_edit_requested)
        self.view.delete_requested.connect(self.on_delete_requested)
        self.view.save_requested.connect(self.on_save_requested)
        self.view.cancel_requested.connect(self.on_cancel_requested)

        # Initial view update
        self.update_view()

    def get_all_customers(self):
        customers = []
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM customers")
            customers = cursor.fetchall()
            conn.close()
        return customers

    def update_view(self):
        self.view.display_customers(self.get_all_customers())

    def on_add_requested(self):
        self.current_edit_index = -1
        self.view.show_form()

    def on_edit_requested(self, index):
        self.current_edit_index = index
        customers = self.get_all_customers()
        if 0 <= index < len(customers):
            customer_data = customers[index]
            self.view.show_form(customer_data)

    def on_delete_requested(self, index):
        reply = QMessageBox.question(
            self.view, 'Delete Customer',
            'Are you sure you want to delete this customer?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            customers = self.get_all_customers()
            if 0 <= index < len(customers):
                customer_id = customers[index]['id']
                conn = get_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM customers WHERE id=%s", (customer_id,))
                    conn.commit()
                    conn.close()
                    self.update_view()

    def on_save_requested(self, data):
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            if self.current_edit_index == -1:
                cursor.execute(
                    "INSERT INTO customers (name, email, phone) VALUES (%s, %s, %s)",
                    (data['name'], data['email'], data['phone'])
                )
            else:
                customers = self.get_all_customers()
                if 0 <= self.current_edit_index < len(customers):
                    customer_id = customers[self.current_edit_index]['id']
                    cursor.execute(
                        "UPDATE customers SET name=%s, email=%s, phone=%s WHERE id=%s",
                        (data['name'], data['email'], data['phone'], customer_id)
                    )
            conn.commit()
            conn.close()
            self.update_view()
        self.view.show_table()

    def on_cancel_requested(self):
        self.view.show_table()
