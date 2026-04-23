from .apiClient import get_stats

class OverviewController:
    def __init__(self, view):
        self.view = view
        self.view.filter_button.clicked.connect(self.update_view)

    def update_view(self):
        start_date = self.view.start_date_edit.date()
        end_date = self.view.end_date_edit.date()
        
        if start_date > end_date:
            self.view.display_stats(0, 0.0)
            return
            
        stats = get_stats(start_date.toString("yyyy-MM-dd"), end_date.toString("yyyy-MM-dd"))
        if stats and isinstance(stats, dict):
            total_products = stats.get('total_products', 0)
            total_revenue = stats.get('total_revenue', 0.0)
            self.view.display_stats(total_products, total_revenue)
        else:
            self.view.display_stats(0, 0.0)
