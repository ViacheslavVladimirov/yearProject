from PyQt6.QtWidgets import QMessageBox
from .apiClient import get_all_customers, create_customer, update_customer, delete_customer
from models.customer import Customer

class CustomerController:
    def __init__(self, view):
        self.view = view
        self.status_callback = lambda m, e=False: None

        # Connect view signals to controller actions
        self.view.add_requested.connect(self.on_add_requested)
        self.view.edit_requested.connect(self.on_edit_requested)
        self.view.delete_requested.connect(self.on_delete_requested)
        self.view.save_requested.connect(self.on_save_requested)
        self.view.cancel_requested.connect(self.on_cancel_requested)

    def update_view(self):
        raw_customers = get_all_customers() or []
        customers = [Customer.deserialize(c).serialize() for c in raw_customers]
        self.view.display_customers(customers)

    def on_add_requested(self):
        self.current_edit_index = -1
        self.view.show_form()

    def on_edit_requested(self, index):
        self.current_edit_index = index
        raw_customers = get_all_customers()
        if raw_customers and 0 <= index < len(raw_customers):
            customer_data = Customer.deserialize(raw_customers[index]).serialize()
            self.view.show_form(customer_data)

    def on_delete_requested(self, index):
        reply = QMessageBox.question(
            self.view, 'Delete Customer',
            'Are you sure you want to delete this customer?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            raw_customers = get_all_customers()
            if raw_customers and 0 <= index < len(raw_customers):
                customer_id = raw_customers[index]['id']
                success = delete_customer(customer_id)
                if success:
                    self.status_callback("Customer deleted successfully")
                else:
                    self.status_callback("Failed to delete customer", True)
                self.update_view()

    def on_save_requested(self, data):
        customer = Customer.deserialize(data)
        payload = customer.serialize()
        if self.current_edit_index == -1:
            success = create_customer(payload)
            if success:
                self.status_callback("Customer created successfully")
            else:
                self.status_callback("Failed to create customer", True)
        else:
            raw_customers = get_all_customers()
            if raw_customers and 0 <= self.current_edit_index < len(raw_customers):
                customer_id = raw_customers[self.current_edit_index]['id']
                success = update_customer(customer_id, payload)
                if success:
                    self.status_callback("Customer updated successfully")
                else:
                    self.status_callback("Failed to update customer", True)
        self.update_view()
        self.view.show_table()

    def on_cancel_requested(self):
        self.view.show_table()
