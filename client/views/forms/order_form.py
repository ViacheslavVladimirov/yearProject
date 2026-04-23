from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QHeaderView, 
    QAbstractItemView, QFormLayout, QComboBox, 
    QDateEdit, QDialog, QLineEdit, QLabel, QCompleter, QCheckBox,
    QMessageBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QIntValidator

class OrderItemDialog(QDialog):
    def __init__(self, parent=None, products=None):
        super().__init__(parent)
        self.setWindowTitle("Add Order Item")
        self.products = products or []
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)

        self.product_combo = QComboBox()
        self.product_combo.setEditable(True)
        self.product_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.product_combo.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.product_combo.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        
        for p in self.products:
            self.product_combo.addItem(p['name'], p)

        self.price_input = QLineEdit()
        self.price_input.setReadOnly(True)

        self.stock_input = QLineEdit()
        self.stock_input.setReadOnly(True)
        
        self.amount_input = QLineEdit()
        self.amount_input.setText("1")
        self.amount_input.setValidator(QIntValidator(1, 9999))

        layout.addRow("Product:", self.product_combo)
        layout.addRow("Price:", self.price_input)
        layout.addRow("Available Stock:", self.stock_input)
        layout.addRow("Amount:", self.amount_input)

        self.product_combo.currentIndexChanged.connect(self.update_product_info)
        self.product_combo.currentTextChanged.connect(self.update_product_info)
        self.update_product_info()

        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Add")
        self.cancel_btn = QPushButton("Cancel")
        
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addRow(button_layout)

    def update_product_info(self):
        product = self.product_combo.currentData()
        if product:
            self.price_input.setText(str(product.get('price', 0.0)))
            self.stock_input.setText(str(product.get('stock', 0)))
        else:
            self.price_input.setText("")
            self.stock_input.setText("")

    def accept(self):
        product = self.product_combo.currentData()
        if not product:
            QMessageBox.warning(self, "Error", "Please select a valid product.")
            return

        try:
            amount = int(self.amount_input.text())
            stock = int(product.get('stock', 0))
            if amount > stock:
                QMessageBox.warning(self, "Insufficient Stock", f"Only {stock} items available in stock.")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid amount.")
            return

        super().accept()

    def get_data(self):
        product = self.product_combo.currentData()
        return {
            'product_id': product.get('id') if product else None,
            'name': self.product_combo.currentText(),
            'price': self.price_input.text(),
            'amount': self.amount_input.text()
        }

class OrderForm(QWidget):
    def __init__(self, on_save, on_cancel, on_collect=None):
        super().__init__()
        self.on_save_callback = on_save
        self.on_cancel_callback = on_cancel
        self.on_collect_callback = on_collect
        self.products = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.customer_combo = QComboBox()
        self.customer_combo.setEditable(True)
        self.customer_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.customer_combo.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.customer_combo.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["None", "Cash", "Payconic", "Split"])
        self.delivered_checkbox = QCheckBox("Delivered")

        self.payment_combo.currentIndexChanged.connect(self.update_delivered_status)

        form_layout.addRow("Date:", self.date_input)
        form_layout.addRow("Customer:", self.customer_combo)
        form_layout.addRow("Payment Method:", self.payment_combo)
        form_layout.addRow(self.delivered_checkbox)
        
        self.total_price_label = QLabel("€ 0.00")
        self.total_price_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        form_layout.addRow("Total Price:", self.total_price_label)
        
        layout.addLayout(form_layout)

        layout.addWidget(QLabel("Order Items:"))
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4) # Added hidden column for product_id
        self.items_table.setHorizontalHeaderLabels(["Name", "Price", "Amount", "product_id"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.items_table.setColumnHidden(3, True)
        self.items_table.verticalHeader().hide()
        self.items_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.items_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        layout.addWidget(self.items_table)

        self.item_btn_container = QWidget()
        item_btn_layout = QHBoxLayout(self.item_btn_container)
        item_btn_layout.setContentsMargins(0, 0, 0, 0)
        self.add_item_btn = QPushButton("Add Item")
        self.remove_item_btn = QPushButton("Remove Item")
        self.add_item_btn.clicked.connect(self.on_add_item)
        self.remove_item_btn.clicked.connect(self.remove_item)
        item_btn_layout.addWidget(self.add_item_btn)
        item_btn_layout.addWidget(self.remove_item_btn)
        layout.addWidget(self.item_btn_container)

        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.collect_btn = QPushButton("Collect Order")
        self.cancel_btn = QPushButton("Cancel")
        self.close_btn = QPushButton("Close")
        
        self.save_btn.clicked.connect(self.on_save_callback)
        self.collect_btn.clicked.connect(self.on_collect_callback)
        self.cancel_btn.clicked.connect(self.on_cancel_callback)
        self.close_btn.clicked.connect(self.on_cancel_callback)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.collect_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)

    def set_read_only(self, read_only):
        self.date_input.setReadOnly(read_only)
        self.customer_combo.setEnabled(not read_only)
        self.payment_combo.setEnabled(not read_only)
        self.delivered_checkbox.setEnabled(not read_only and self.payment_combo.currentText() != "None")
        self.items_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers if read_only else QAbstractItemView.EditTrigger.DoubleClicked)
        
        self.item_btn_container.setVisible(not read_only)
        self.save_btn.setVisible(not read_only)
        self.cancel_btn.setVisible(not read_only)
        self.close_btn.setVisible(read_only)
        self.collect_btn.setVisible(read_only)
        
        if read_only:
            is_delivered = self.delivered_checkbox.isChecked()
            self.collect_btn.setEnabled(not is_delivered)

    def on_add_item(self):
        dialog = OrderItemDialog(self, self.products)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            row = self.items_table.rowCount()
            self.items_table.insertRow(row)
            self.items_table.setItem(row, 0, QTableWidgetItem(str(data['name'])))
            self.items_table.setItem(row, 1, QTableWidgetItem(str(data['price'])))
            self.items_table.setItem(row, 2, QTableWidgetItem(str(data['amount'])))
            self.items_table.setItem(row, 3, QTableWidgetItem(str(data['product_id'])))
            self.calculate_total()

    def remove_item(self):
        selected_row = self.items_table.currentRow()
        if selected_row >= 0:
            self.items_table.removeRow(selected_row)
            self.calculate_total()

    def calculate_total(self):
        total = 0.0
        for row in range(self.items_table.rowCount()):
            try:
                price = float(self.items_table.item(row, 1).text())
                amount = int(self.items_table.item(row, 2).text())
                total += price * amount
            except (ValueError, AttributeError, TypeError):
                continue
        self.total_price_label.setText(f"€ {total:.2f}")
        return total

    def update_delivered_status(self):
        is_paid = self.payment_combo.currentText() != "None"
        self.delivered_checkbox.setEnabled(is_paid)
        if not is_paid:
            self.delivered_checkbox.setChecked(False)

    def set_data(self, order_data, customers, products):
        self.customer_combo.clear()
        for c in customers:
            self.customer_combo.addItem(c['name'], c['id'])
        
        self.products = products
        self.items_table.setRowCount(0)
        
        if order_data:
            date_str = order_data.get('date', '')
            if date_str:
                self.date_input.setDate(QDate.fromString(date_str, Qt.DateFormat.ISODate))

            cid = order_data.get('customer_id')
            cname = order_data.get('customer', '')
            index = self.customer_combo.findData(cid)
            if index < 0 and cid is not None:
                self.customer_combo.addItem(f"{cname} (Inactive)", cid)
                index = self.customer_combo.findData(cid)
            
            if index >= 0:
                self.customer_combo.setCurrentIndex(index)
            
            p_index = self.payment_combo.findText(order_data.get('payment', ''))
            if p_index >= 0:
                self.payment_combo.setCurrentIndex(p_index)
            
            self.delivered_checkbox.setChecked(bool(order_data.get('is_delivered', False)))

            items = order_data.get('items', [])
            for row, item in enumerate(items):
                self.items_table.insertRow(row)
                self.items_table.setItem(row, 0, QTableWidgetItem(str(item.get('name', ''))))
                self.items_table.setItem(row, 1, QTableWidgetItem(str(item.get('price', ''))))
                self.items_table.setItem(row, 2, QTableWidgetItem(str(item.get('amount', ''))))
                self.items_table.setItem(row, 3, QTableWidgetItem(str(item.get('product_id', ''))))
            
            self.calculate_total()
            self.update_delivered_status()
        else:
            self.date_input.setDate(QDate.currentDate())
            self.payment_combo.setCurrentIndex(0)
            self.calculate_total()
            self.update_delivered_status()

    def get_data(self):
        items = []
        for row in range(self.items_table.rowCount()):
            items.append({
                'name': self.items_table.item(row, 0).text(),
                'price': self.items_table.item(row, 1).text(),
                'amount': self.items_table.item(row, 2).text(),
                'product_id': self.items_table.item(row, 3).text()
            })
        return {
            'date': self.date_input.date().toString(Qt.DateFormat.ISODate),
            'customer_id': self.customer_combo.currentData(),
            'payment': self.payment_combo.currentText(),
            'is_delivered': self.delivered_checkbox.isChecked(),
            'total': self.calculate_total(),
            'items': items
        }

class PaymentDialog(QDialog):
    def __init__(self, parent=None, current_payment="None"):
        super().__init__(parent)
        self.setWindowTitle("Select Payment Method")
        self.setup_ui(current_payment)

    def setup_ui(self, current_payment):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["None", "Cash", "Payconic", "Split"])
        
        index = self.payment_combo.findText(current_payment)
        if index >= 0:
            self.payment_combo.setCurrentIndex(index)
            
        form_layout.addRow("Payment Method:", self.payment_combo)
        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.payment_combo.currentIndexChanged.connect(self.update_save_button)
        self.update_save_button()

    def update_save_button(self):
        self.save_btn.setEnabled(self.payment_combo.currentText() != "None")

    def get_payment_method(self):
        return self.payment_combo.currentText()
