from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QFrame
from PyQt6.QtCore import Qt

class OverviewTab(QWidget):
    def __init__(self, get_orders_callback=None):
        super().__init__()
        self.get_orders_callback = get_orders_callback
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Business Overview")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)

        grid = QGridLayout()
        
        # Products Sold Card
        self.products_sold_label = QLabel("0")
        grid.addWidget(self.create_stat_card("Products Sold", self.products_sold_label), 0, 0)
        
        # Total Revenue Card
        self.revenue_label = QLabel("€ 0.00")
        grid.addWidget(self.create_stat_card("Total Revenue", self.revenue_label), 0, 1)
        
        layout.addLayout(grid)
        layout.addStretch()

    def create_stat_card(self, title, value_label):
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("background-color: #f0f0f0; border-radius: 10px; padding: 20px;")
        
        layout = QVBoxLayout(frame)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; color: #666;")
        layout.addWidget(title_label)
        
        value_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #333;")
        layout.addWidget(value_label)
        
        return frame

    def refresh(self):
        """Updates statistics based on current orders."""
        if not self.get_orders_callback:
            return

        orders = self.get_orders_callback()
        total_products = 0
        total_revenue = 0.0

        for order in orders:
            # We only count delivered/paid orders for revenue usually, 
            # but here we'll count all existing ones as per "transactions"
            items = order.get('items', [])
            for item in items:
                try:
                    amount = int(item.get('amount', 0))
                    price = float(item.get('price', 0))
                    total_products += amount
                    total_revenue += amount * price
                except ValueError:
                    continue

        self.products_sold_label.setText(str(total_products))
        self.revenue_label.setText(f"€ {total_revenue:.2f}")
