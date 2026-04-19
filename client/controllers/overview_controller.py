from .db_utils import get_connection

class OverviewController:
    def __init__(self, view):
        self.view = view
        self.update_view()

    def update_view(self):
        total_products = 0
        total_revenue = 0.0
        
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            # We can calculate stats directly in SQL for efficiency, 
            # but for now we'll fetch items and sum them to match previous logic
            cursor.execute("SELECT amount, price FROM order_items")
            items = cursor.fetchall()
            
            for item in items:
                try:
                    amount = int(item.get('amount', 0))
                    price = float(item.get('price', 0))
                    total_products += amount
                    total_revenue += amount * price
                except (ValueError, TypeError):
                    continue
            conn.close()

        self.view.display_stats(total_products, total_revenue)
