class OrderController:
    def __init__(self, model, view, customer_model, product_model):
        self.model = model
        self.view = view
        self.customer_model = customer_model
        self.product_model = product_model

        self.model.on_data_changed.append(self.update_view)

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
