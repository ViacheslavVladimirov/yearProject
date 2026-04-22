from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class EmptyMenuView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.message_label = QLabel("No connection to server.\nPlease check if the server is running.")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("font-size: 18px; color: #666; font-weight: bold;")
        
        layout.addStretch()
        layout.addWidget(self.message_label)
        layout.addStretch()
