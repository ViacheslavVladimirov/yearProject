from .db_utils import get_stats

class OverviewController:
    def __init__(self, view):
        self.view = view
        self.update_view()

    def update_view(self):
        stats = get_stats()
        if stats:
            total_products = stats.get('total_products', 0)
            total_revenue = stats.get('total_revenue', 0.0)
            self.view.display_stats(total_products, total_revenue)
        else:
            self.view.display_stats(0, 0.0)
