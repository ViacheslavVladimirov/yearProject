from .apiClient import get_all_orders, create_order, update_order, get_all_customers, get_all_products

class OrderController:
    def __init__(self, view, customer_view, product_view):
        self.view = view
        self.customer_view = customer_view
        self.product_view = product_view
        self.status_callback = lambda m, e=False: None
        
        self.on_orders_changed_callbacks = []
        self.current_order_id = None

        self.view.add_requested.connect(self.on_add_requested)
        self.view.view_requested.connect(self.on_view_requested)
        self.view.save_requested.connect(self.on_save_requested)
        self.view.cancel_requested.connect(self.on_cancel_requested)
        self.view.collect_requested.connect(self.on_collect_requested)

    def _handle_api_response(self, response, success_msg):
        if isinstance(response, str) and response.startswith("ERROR"):
            self.status_callback(response, True)
            return None
        if response is True or isinstance(response, (list, dict)):
            if success_msg:
                self.status_callback(success_msg)
            return response
        return None

    def get_orders_processed(self):
        response = get_all_orders()
        raw_orders = self._handle_api_response(response, None)
        if raw_orders is None:
            return []
            
        orders = []
        for ro in raw_orders:
            data = {
                'id': ro.get('id'),
                'date': str(ro.get('order_date', '')),
                'customer': ro.get('customer_name', ''),
                'payment': ro.get('payment_method', ''),
                'is_delivered': bool(ro.get('is_delivered', False)),
                'total': float(ro.get('total_price', 0.0))
            }

            processed_items = []
            for item in ro.get('items', []):
                processed_items.append({
                    'name': item.get('product_name', ''),
                    'price': float(item.get('price', 0.0)),
                    'amount': int(item.get('amount', 0))
                })
            data['items'] = processed_items
            orders.append(data)
        return orders

    def update_view(self):
        orders = self.get_orders_processed()
        self.view.display_orders(orders)
        for callback in self.on_orders_changed_callbacks:
            callback()

    def on_add_requested(self):
        self.current_order_id = None
        
        c_res = get_all_customers()
        raw_customers = self._handle_api_response(c_res, None) or []
        customers = [c.get('name', '') for c in raw_customers]
        
        p_res = get_all_products()
        raw_products = self._handle_api_response(p_res, None) or []
        
        self.view.show_form(None, customers, raw_products)

    def on_view_requested(self, order_id):
        self.current_order_id = order_id
        orders = self.get_orders_processed()
        order_data = next((o for o in orders if o['id'] == order_id), None)
        
        if order_data:
            c_res = get_all_customers()
            raw_customers = self._handle_api_response(c_res, None) or []
            customers = [c.get('name', '') for c in raw_customers]
            
            p_res = get_all_products()
            raw_products = self._handle_api_response(p_res, None) or []
            
            self.view.show_view_mode(order_data, customers, raw_products)

    def on_save_requested(self, data):
        items = []
        for item in data.get('items', []):
            items.append({
                'product_name': item['name'],
                'price': item['price'],
                'amount': item['amount']
            })
        
        payload = {
            'date': data['date'],
            'customer': data['customer'],
            'payment': data['payment'],
            'is_delivered': data['is_delivered'],
            'total': data['total'],
            'items': items
        }

        if self.current_order_id is None:
            res = create_order(payload)
            if self._handle_api_response(res, "Order created successfully"):
                self.update_view()
                self.view.show_table()
        else:
            res = update_order(self.current_order_id, payload)
            if self._handle_api_response(res, "Order updated successfully"):
                self.update_view()
                self.view.show_table()

    def on_cancel_requested(self):
        self.view.show_table()

    def on_collect_requested(self):
        if self.current_order_id is not None:
            orders = self.get_orders_processed()
            order_data = next((o for o in orders if o['id'] == self.current_order_id), None)
            
            if order_data:
                current_payment = order_data.get('payment', 'None')
                
                if current_payment == "None" or not current_payment:
                    payment = self.view.show_payment_dialog(current_payment)
                    if payment:
                        current_payment = payment
                    else:
                        return

                order_data['payment'] = current_payment
                order_data['is_delivered'] = True

                items = []
                for item in order_data.get('items', []):
                    items.append({
                        'product_name': item['name'],
                        'price': item['price'],
                        'amount': item['amount']
                    })

                payload = {
                    'date': order_data['date'],
                    'customer': order_data['customer'],
                    'payment': order_data['payment'],
                    'is_delivered': order_data['is_delivered'],
                    'total': order_data['total'],
                    'items': items
                }
                
                res = update_order(order_data['id'], payload)
                if self._handle_api_response(res, "Order collected and paid successfully"):
                    self.update_view()

                    c_res = get_all_customers()
                    raw_customers = self._handle_api_response(c_res, None) or []
                    customers = [c.get('name', '') for c in raw_customers]
                    
                    p_res = get_all_products()
                    raw_products = self._handle_api_response(p_res, None) or []
                    
                    self.view.show_view_mode(order_data, customers, raw_products)
