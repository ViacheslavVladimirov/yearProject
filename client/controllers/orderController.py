from .apiClient import get_all_orders, create_order, update_order, get_all_customers, get_all_products
from models.order import Order
from models.customer import Customer
from models.product import Product

class OrderController:
    def __init__(self, view, customer_view, product_view):
        self.view = view
        self.customer_view = customer_view
        self.product_view = product_view
        
        self.on_orders_changed_callbacks = []

        self.view.add_requested.connect(self.on_add_requested)
        self.view.view_requested.connect(self.on_view_requested)
        self.view.save_requested.connect(self.on_save_requested)
        self.view.cancel_requested.connect(self.on_cancel_requested)
        self.view.collect_requested.connect(self.on_collect_requested)

    def get_orders_processed(self):
        raw_orders = get_all_orders() or []
        orders = []
        for ro in raw_orders:
            order_obj = Order.deserialize(ro)
            # Add fields for UI display that aren't in the model but derived
            # Or ensure model has them.
            data = order_obj.serialize()
            data['date'] = str(ro.get('order_date', ''))
            data['customer'] = ro.get('customer_name', '')
            data['payment'] = ro.get('payment_method', '')
            data['is_delivered'] = bool(ro.get('is_delivered', False))
            data['total'] = float(ro.get('total_price', 0.0))
            
            # Map item keys for UI
            processed_items = []
            for item in ro.get('items', []):
                processed_items.append({
                    'name': item.get('product_name', ''),
                    'price': item.get('price', 0.0),
                    'amount': item.get('amount', 0)
                })
            data['items'] = processed_items
            orders.append(data)
        return orders

    def update_view(self):
        self.view.display_orders(self.get_orders_processed())
        for callback in self.on_orders_changed_callbacks:
            callback()

    def on_add_requested(self):
        self.current_edit_index = -1
        raw_customers = get_all_customers() or []
        customers = [Customer.deserialize(c).name for c in raw_customers]
        raw_products = get_all_products() or []
        products = [Product.deserialize(p).serialize() for p in raw_products]
        self.view.show_form(None, customers, products)

    def on_view_requested(self, index):
        self.current_edit_index = index
        orders = self.get_orders_processed()
        if 0 <= index < len(orders):
            order_data = orders[index]
            raw_customers = get_all_customers() or []
            customers = [Customer.deserialize(c).name for c in raw_customers]
            raw_products = get_all_products() or []
            products = [Product.deserialize(p).serialize() for p in raw_products]
            self.view.show_view_mode(order_data, customers, products)

    def on_save_requested(self, data):
        # Remap from view format to model/server format
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

        if self.current_edit_index == -1:
            create_order(payload)
        else:
            orders = self.get_orders_processed()
            if 0 <= self.current_edit_index < len(orders):
                order_id = orders[self.current_edit_index]['id']
                update_order(order_id, payload)
        
        self.update_view()
        self.view.show_table()

    def on_cancel_requested(self):
        self.view.show_table()

    def on_collect_requested(self):
        if self.current_edit_index >= 0:
            orders = self.get_orders_processed()
            if self.current_edit_index < len(orders):
                order_data = orders[self.current_edit_index]
                current_payment = order_data.get('payment', 'None')
                
                if current_payment == "None" or not current_payment:
                    payment = self.view.show_payment_dialog(current_payment)
                    if payment:
                        current_payment = payment
                    else:
                        return

                order_data['payment'] = current_payment
                order_data['is_delivered'] = True
                
                # Payload for server update, remapping items
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
                
                update_order(order_data['id'], payload)
                self.update_view()
                
                # Refresh view mode
                raw_customers = get_all_customers() or []
                customers = [Customer.deserialize(c).name for c in raw_customers]
                raw_products = get_all_products() or []
                products = [Product.deserialize(p).serialize() for p in raw_products]
                self.view.show_view_mode(order_data, customers, products)
