from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QFrame, QHBoxLayout, QDateEdit, QPushButton
from PyQt6.QtCore import Qt, QDate

class OverviewView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Business Overview")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)

        # Date Filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Start Date:"))
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())
        filter_layout.addWidget(self.start_date_edit)

        filter_layout.addWidget(QLabel("End Date:"))
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        filter_layout.addWidget(self.end_date_edit)

        self.filter_button = QPushButton("Filter")
        filter_layout.addWidget(self.filter_button)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

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

    def display_stats(self, total_products, total_revenue):
        self.products_sold_label.setText(str(total_products))
        self.revenue_label.setText(f"€ {total_revenue:.2f}")
