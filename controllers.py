from PyQt6.QtWidgets import QMessageBox, QDialog
from PyQt6.QtCore import Qt

class CustomerController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # Connect model signals to view updates
        self.model.data_changed.connect(self.update_view)

        # Connect view signals to controller actions
        self.view.add_requested.connect(self.on_add_requested)
        self.view.edit_requested.connect(self.on_edit_requested)
        self.view.delete_requested.connect(self.on_delete_requested)
        self.view.save_requested.connect(self.on_save_requested)
        self.view.cancel_requested.connect(self.on_cancel_requested)

        # Initial view update
        self.update_view()

    def update_view(self):
        self.view.display_customers(self.model.get_all())

    def on_add_requested(self):
        self.current_edit_index = -1
        self.view.show_form()

    def on_edit_requested(self, index):
        self.current_edit_index = index
        customer_data = self.model.get_all()[index]
        self.view.show_form(customer_data)

    def on_delete_requested(self, index):
        reply = QMessageBox.question(
            self.view, 'Delete Customer',
            'Are you sure you want to delete this customer?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.model.delete(index)

    def on_save_requested(self, data):
        if self.current_edit_index == -1:
            self.model.add(data)
        else:
            self.model.update(self.current_edit_index, data)
        self.view.show_table()

    def on_cancel_requested(self):
        self.view.show_table()

class ProductController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.model.data_changed.connect(self.update_view)

        self.view.add_requested.connect(self.on_add_requested)
        self.view.edit_requested.connect(self.on_edit_requested)
        self.view.delete_requested.connect(self.on_delete_requested)
        self.view.save_requested.connect(self.on_save_requested)
        self.view.cancel_requested.connect(self.on_cancel_requested)

        self.update_view()

    def update_view(self):
        self.view.display_products(self.model.get_all())

    def on_add_requested(self):
        self.current_edit_index = -1
        self.view.show_form()

    def on_edit_requested(self, index):
        self.current_edit_index = index
        product_data = self.model.get_all()[index]
        self.view.show_form(product_data)

    def on_delete_requested(self, index):
        reply = QMessageBox.question(
            self.view, 'Delete Product',
            'Are you sure you want to delete this product?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.model.delete(index)

    def on_save_requested(self, data):
        if self.current_edit_index == -1:
            self.model.add(data)
        else:
            self.model.update(self.current_edit_index, data)
        self.view.show_table()

    def on_cancel_requested(self):
        self.view.show_table()

class OrderController:
    def __init__(self, model, view, customer_model, product_model):
        self.model = model
        self.view = view
        self.customer_model = customer_model
        self.product_model = product_model

        self.model.data_changed.connect(self.update_view)

        self.view.add_requested.connect(self.on_add_requested)
        self.view.view_requested.connect(self.on_view_requested)
        self.view.save_requested.connect(self.on_save_requested)
        self.view.cancel_requested.connect(self.on_cancel_requested)
        self.view.collect_requested.connect(self.on_collect_requested)

        self.update_view()

    def update_view(self):
        self.view.display_orders(self.model.get_all())

    def on_add_requested(self):
        self.current_edit_index = -1
        customers = [c['name'] for c in self.customer_model.get_all()]
        products = self.product_model.get_all()
        self.view.show_form(None, customers, products)

    def on_view_requested(self, index):
        self.current_edit_index = index
        order_data = self.model.get_all()[index]
        customers = [c['name'] for c in self.customer_model.get_all()]
        products = self.product_model.get_all()
        self.view.show_view_mode(order_data, customers, products)

    def on_save_requested(self, data):
        if self.current_edit_index == -1:
            self.model.add(data)
        else:
            self.model.update(self.current_edit_index, data)
        self.view.show_table()

    def on_cancel_requested(self):
        self.view.show_table()

    def on_collect_requested(self):
        if self.current_edit_index >= 0:
            order_data = self.model.get_all()[self.current_edit_index]
            current_payment = order_data.get('payment', 'None')
            
            if current_payment == "None":
                payment = self.view.show_payment_dialog(current_payment)
                if payment:
                    current_payment = payment
                else:
                    return

            order_data['payment'] = current_payment
            order_data['status'] = "Yes"
            self.model.update(self.current_edit_index, order_data)
            
            # Re-show in view mode to refresh
            customers = [c['name'] for c in self.customer_model.get_all()]
            products = self.product_model.get_all()
            self.view.show_view_mode(order_data, customers, products)

class OverviewController:
    def __init__(self, model, view):
        self.model = model # OrderModel
        self.view = view

        self.model.data_changed.connect(self.update_view)
        self.update_view()

    def update_view(self):
        orders = self.model.get_all()
        total_products = 0
        total_revenue = 0.0

        for order in orders:
            items = order.get('items', [])
            for item in items:
                try:
                    amount = int(item.get('amount', 0))
                    price = float(item.get('price', 0))
                    total_products += amount
                    total_revenue += amount * price
                except ValueError:
                    continue

        self.view.display_stats(total_products, total_revenue)
