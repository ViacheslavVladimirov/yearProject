from PyQt6.QtWidgets import QMessageBox
from .apiClient import get_all_customers, create_customer, update_customer, delete_customer

class CustomerController:
    def __init__(self, view):
        self.view = view
        self.status_callback = lambda m, e=False: None

        self.view.add_requested.connect(self.on_add_requested)
        self.view.edit_requested.connect(self.on_edit_requested)
        self.view.delete_requested.connect(self.on_delete_requested)
        self.view.save_requested.connect(self.on_save_requested)
        self.view.cancel_requested.connect(self.on_cancel_requested)

    def _handle_api_response(self, response, success_msg):
        if isinstance(response, str) and response.startswith("ERROR"):
            self.status_callback(response, True)
            return None
        if response is True or isinstance(response, (list, dict)):
            if success_msg:
                self.status_callback(success_msg)
            return response
        return None

    def update_view(self):
        response = get_all_customers()
        customers = self._handle_api_response(response, None)
        if customers is not None:
            self.view.display_customers(customers)

    def on_add_requested(self):
        self.current_edit_index = -1
        self.view.show_form()

    def on_edit_requested(self, index):
        self.current_edit_index = index
        response = get_all_customers()
        customers = self._handle_api_response(response, None)
        if customers and 0 <= index < len(customers):
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
            response = get_all_customers()
            customers = self._handle_api_response(response, None)
            if customers and 0 <= index < len(customers):
                customer_id = customers[index]['id']
                res = delete_customer(customer_id)
                if self._handle_api_response(res, "Customer deleted successfully"):
                    self.update_view()

    def on_save_requested(self, data):
        payload = {
            "name": data.get("name", ""),
            "email": data.get("email", ""),
            "phone": data.get("phone", "")
        }
        if self.current_edit_index == -1:
            res = create_customer(payload)
            if self._handle_api_response(res, "Customer created successfully"):
                self.update_view()
                self.view.show_table()
        else:
            response = get_all_customers()
            customers = self._handle_api_response(response, None)
            if customers and 0 <= self.current_edit_index < len(customers):
                customer_id = customers[self.current_edit_index]['id']
                res = update_customer(customer_id, payload)
                if self._handle_api_response(res, "Customer updated successfully"):
                    self.update_view()
                    self.view.show_table()

    def on_cancel_requested(self):
        self.view.show_table()
