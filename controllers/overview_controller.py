class OverviewController:
    def __init__(self, model, view):
        self.model = model # Order model
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
