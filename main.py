import sys
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QGridLayout, QHBoxLayout, QVBoxLayout,
    QWidget, QLabel, QToolBar, QFrame, QSpinBox, QScrollArea, QSizePolicy,
    QLineEdit, QStackedWidget, QMessageBox
)
from PyQt6.QtGui import QFont
from datetime import datetime
print("Starting GUI...")

print("Importing controller...")
import controller
import model
print("Initializing controller...")
c = controller.Controller()
print("Controller ready")


# ── Shared helpers ────────────────────────────────────────────────────────────

def make_toolbar(window, navigator):
    """Returns a toolbar with refresh/exit and a clock on the right."""
    refreshButton = QPushButton("refresh")
    exitButton = QPushButton("exit")
    exitButton.clicked.connect(window.close)
    productsButton = QPushButton("manage products")
    productsButton.clicked.connect(lambda: navigator.go_to("product_menu"))

    now = datetime.now()
    clock_lbl = QLabel(f"{now.strftime('%H:%M')}    {now.strftime('%d/%m/%Y')}")
    clock_lbl.setStyleSheet("color: white; padding-right: 10px;")

    toolbar = QToolBar()
    toolbar.addWidget(refreshButton)
    toolbar.addWidget(exitButton)
    toolbar.addWidget(productsButton)
    spacer = QWidget()
    spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    toolbar.addWidget(spacer)
    toolbar.addWidget(clock_lbl)
    toolbar.setStyleSheet("""
        QToolBar { background-color: #444; spacing: 10px; }
        QPushButton { color: white; border: 1px solid white; padding: 3px 8px; background-color: transparent; }
    """)
    return toolbar


def make_orders_panel_frame():
    """Returns the right-side 'Current orders' panel."""
    order_panel = QFrame()
    order_panel.setStyleSheet("background-color: #3f4c56; border: 1px solid #555;")
    order_layout = QVBoxLayout()
    order_layout.setContentsMargins(8, 8, 8, 8)
    order_layout.setSpacing(6)
    order_panel.setLayout(order_layout)

    header_row = QHBoxLayout()
    collapse_btn = QPushButton("−")
    collapse_btn.setFixedSize(20, 20)
    collapse_btn.setStyleSheet("color: white; background-color: #2f3c48; border: 1px solid #666; font-weight: bold; padding: 0;")
    current_lbl = QLabel("Current orders")
    current_lbl.setFont(QFont("Arial", 10, QFont.Weight.Bold))
    current_lbl.setStyleSheet("color: white; background-color: transparent; border: none;")
    header_row.addWidget(collapse_btn)
    header_row.addWidget(current_lbl)
    header_row.addStretch()
    order_layout.addLayout(header_row)

    return order_panel, order_layout


def btn_style():
    return "color: white; border: 1px solid white; padding: 6px 15px; background-color: #3f4c56;"

class OrderLine(QPushButton):
    def __init__(self, sale_id, customer_name, isPaid, total, date, on_click):
        super().__init__()
        self.sale_id = sale_id
        self.customer_name = customer_name
        self.isPaid = isPaid
        self.total = total
        self.date = date
        self.setText(f"{customer_name}    {date}")
        self.setStyleSheet("background-color: #2f2b6b; color: white; border: none; padding: 8px; text-align: left;")
        self.clicked.connect(lambda: on_click(self))

# ── Screens ───────────────────────────────────────────────────────────────────

class MainMenuScreen(QWidget):
    def __init__(self, navigator):
        super().__init__()
        self.navigator = navigator
        self.c = c

        layout = QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)

        # Left panel
        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: #3a3a3a; border: 1px solid #555;")
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 10)
        left_layout.setSpacing(8)
        left_panel.setLayout(left_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")
        product_container = QWidget()
        product_container.setStyleSheet("background-color: #2e2e2e;")
        container_layout = QVBoxLayout()
        container_layout.setSpacing(5)
        container_layout.setContentsMargins(8, 8, 8, 8)
        product_container.setLayout(container_layout)
        # for name, avail, price in [("Product 1", 10, "$4,50"), ("Product 2", 3, "$10"), ("Product 3", 5, "$14,99")]:
        #     container_layout.addWidget(ProductRow(name, avail, price))
        for name, price, stock, id in c.listProducts():
            container_layout.addWidget(ProductRow(str(name), str(price), str(stock)))
        container_layout.addStretch()
        scroll.setWidget(product_container)
        left_layout.addWidget(scroll)

        total_lbl = QLabel("total: $0")
        total_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        total_lbl.setStyleSheet("color: white; background-color: #3f4c56; border: 1px solid #666; padding: 6px;")
        total_lbl.setFixedWidth(160)
        total_wrapper = QHBoxLayout()
        total_wrapper.addStretch()
        total_wrapper.addWidget(total_lbl)
        total_wrapper.addStretch()
        left_layout.addLayout(total_wrapper)

        button_frame = QFrame()
        button_frame.setStyleSheet("background-color: transparent; border: none;")
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(10, 0, 10, 0)
        button_frame.setLayout(button_layout)

        place_btn = QPushButton("place order")
        place_btn.clicked.connect(lambda: navigator.go_to("order_menu"))
        sell_btn = QPushButton("sell")
        sell_btn.clicked.connect(lambda: navigator.go_to("sale_menu"))
        cancel_btn = QPushButton("cancel")
        for btn in [place_btn, sell_btn, cancel_btn]:
            btn.setStyleSheet(btn_style())
        button_layout.addWidget(place_btn)
        button_layout.addWidget(sell_btn)
        button_layout.addWidget(cancel_btn)
        left_layout.addWidget(button_frame)

        layout.addWidget(left_panel, 0, 0)

        self.orders_panel, self.orders_layout = make_orders_panel_frame()
        layout.addWidget(self.orders_panel, 0, 1)

        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 1)

        self.refresh_orders()

    def showEvent(self, event):
        self.refresh_orders()

    def refresh_orders(self):
        while self.orders_layout.count() > 1:
            item = self.orders_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for sale_id, customer_name, isPaid, total, date in self.c.listOrders():
            self.orders_layout.insertWidget(
                0,
                OrderLine(sale_id, customer_name, isPaid, total, date, self.on_order_clicked)
            )
    
    def on_order_clicked(self, order_line):
        detail_screen = self.navigator.screens["order_detail"]
        detail_screen.load_order(
            customer_name=order_line.customer_name,
            date=order_line.date,
            items= self.c.getSaleLines(order_line.sale_id),
            total=order_line.total,
            isPaid=order_line.isPaid,
            id=order_line.sale_id
        )
        self.navigator.go_to("order_detail")


class SaleMenuScreen(QWidget):
    def __init__(self, navigator):
        super().__init__()
        self.navigator = navigator
        self.c = c
        

        layout = QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)

        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: #3a3a3a; border: 1px solid #555;")
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 10)
        left_layout.setSpacing(8)
        left_panel.setLayout(left_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")
        items_container = QWidget()
        items_container.setStyleSheet("background-color: #2e2e2e;")
        self.items_layout = QVBoxLayout()
        self.items_layout.setSpacing(2)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        items_container.setLayout(self.items_layout)

        totalPrice = 0
        for item in self.c.current_operation:
            self.items_layout.addWidget(ProductItemRow(item["product"].name, item["quantity"]))
            totalPrice += item["product"].price * item["quantity"]
        self.items_layout.addStretch()
        
        scroll.setWidget(items_container)
        left_layout.addWidget(scroll)

        ct_layout = QHBoxLayout()
        ct_layout.setContentsMargins(10, 0, 10, 0)
        ct_layout.setSpacing(10)
        self.customer_lbl = QLabel("No customer selected")
        self.customer_lbl.setStyleSheet(btn_style())
        self.total_lbl = QLabel(f"total: ${totalPrice}")
        self.total_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_lbl.setStyleSheet("color: white; background-color: #3f4c56; border: 1px solid #666; padding: 6px;")
        ct_layout.addWidget(self.customer_lbl)
        ct_layout.addWidget(self.total_lbl)
        left_layout.addLayout(ct_layout)

        button_frame = QFrame()
        button_frame.setStyleSheet("background-color: transparent; border: none;")
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(10, 0, 10, 0)
        button_frame.setLayout(button_layout)
        find_btn = QPushButton("find custommer")
        find_btn.clicked.connect(lambda: navigator.go_to("customer_menu"))
        sell_btn = QPushButton("sell")
        sell_btn.clicked.connect(self.on_sale_clicked)
        cancel_btn = QPushButton("cancel")
        cancel_btn.clicked.connect(self.reset_sale)
        for btn in [find_btn, sell_btn, cancel_btn]:
            btn.setStyleSheet(btn_style())
        button_layout.addWidget(find_btn)
        button_layout.addWidget(sell_btn)
        button_layout.addWidget(cancel_btn)
        left_layout.addWidget(button_frame)

        layout.addWidget(left_panel, 0, 0)

        self.orders_panel, self.orders_layout = make_orders_panel_frame()
        layout.addWidget(self.orders_panel, 0, 1)

        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 1)

    def showEvent(self, event):
        customer = self.c.selected_customer
        self.refresh()
        self.refresh_orders()

        if customer:
            name = customer[0]
            self.customer_lbl.setText(name)

    def refresh(self):
        while self.items_layout.count() > 1:
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        total = 0
        for item in self.c.current_operation:
            self.items_layout.insertWidget(self.items_layout.count() - 1, ProductItemRow(item["product"].name, item["quantity"]))
            total += item["product"].price * item["quantity"]

        self.total_lbl.setText(f"total: ${total:.2f}")
        if self.c.selected_customer:
            self.customer_lbl.setText(self.c.selected_customer[0])
        else:
            self.customer_lbl.setText("No customer selected")

    def reset_sale(self):
        self.c.selected_customer = None
        self.c.clearOperation()
        self.customer_lbl.setText("No customer selected")
        self.navigator.go_to("main_menu")

    def refresh_orders(self):
        while self.orders_layout.count() > 1:
            item = self.orders_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for sale_id, customer_name, isPaid, total, date in self.c.listOrders():
            self.orders_layout.insertWidget(
                0,
                OrderLine(sale_id, customer_name, isPaid, total, date, self.on_order_clicked)
            )

    def on_order_clicked(self, order_line):
        detail_screen = self.navigator.screens["order_detail"]
        detail_screen.load_order(
            customer_name=order_line.customer_name,
            date=order_line.date,
            items= self.c.getSaleLines(order_line.sale_id),
            total=order_line.total,
            isPaid=order_line.isPaid,
            id=order_line.sale_id
        )
        self.navigator.go_to("order_detail")

    def on_sale_clicked(self):
        total = sum(item["product"].price * item["quantity"] for item in self.c.current_operation)
        payment_screen = self.navigator.screens["payment_menu"]
        payment_screen.load_payment(total=total, return_screen="sale_menu", isSale=True)
        self.navigator.go_to("payment_menu")

class CustomerMenuScreen(QWidget):
    def __init__(self, navigator):
        super().__init__()
        self.navigator = navigator
        self.c = c
        self.selected_customer_row = None

        layout = QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)

        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: #3a3a3a; border: 1px solid #555;")
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 10)
        left_layout.setSpacing(8)
        left_panel.setLayout(left_layout)

        list_frame = QFrame()
        list_frame.setStyleSheet("background-color: #2e2e2e; border: none;")
        list_layout = QVBoxLayout()
        list_layout.setContentsMargins(8, 8, 8, 8)
        list_layout.setSpacing(5)
        list_frame.setLayout(list_layout)

        search_input = QLineEdit()
        search_input.setPlaceholderText("search")
        search_input.setStyleSheet("background-color: #4a4a4a; color: white; border: 1px solid #666; padding: 5px;")
        list_layout.addWidget(search_input)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")
        customers_container = QWidget()
        customers_container.setStyleSheet("background-color: transparent;")
        self.customers_layout = QVBoxLayout()
        self.customers_layout.setSpacing(3)
        self.customers_layout.setContentsMargins(0, 0, 0, 0)
        customers_container.setLayout(self.customers_layout)

        for name, email, id in c.listCustomers():
            self.customers_layout.addWidget(CustomerRow(str(name), str(email), id, self))
            
        self.customers_layout.addStretch()
        scroll.setWidget(customers_container)
        list_layout.addWidget(scroll)
        left_layout.addWidget(list_frame, 1)

        button_frame = QFrame()
        button_frame.setStyleSheet("background-color: transparent; border: none;")
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(10, 0, 10, 0)
        button_frame.setLayout(button_layout)
        register_btn = QPushButton("register custommer")
        register_btn.clicked.connect(lambda: navigator.go_to("customer_register_edit_menu"))
        edit_btn = QPushButton("edit")
        edit_btn.clicked.connect(self.edit_customer)
        add_btn = QPushButton("add")
        add_btn.clicked.connect(self.add_customer_to_operation)
        back_btn = QPushButton("back")
        back_btn.clicked.connect(lambda: navigator.go_back())
        for btn in [register_btn, edit_btn, add_btn, back_btn]:
            btn.setStyleSheet(btn_style())
        button_layout.addWidget(register_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(add_btn)
        button_layout.addWidget(back_btn)
        left_layout.addWidget(button_frame)

        layout.addWidget(left_panel, 0, 0)

        self.orders_panel, self.orders_layout = make_orders_panel_frame()
        layout.addWidget(self.orders_panel, 0, 1)

        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 1)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_customers()
        self.refresh_orders()

    def refresh_customers(self):
        self.selected_customer_row = None

        while self.customers_layout.count():
            item = self.customers_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for name, email, id in self.c.listCustomers():
            self.customers_layout.addWidget(CustomerRow(name, email, id, self))
        self.customers_layout.addStretch()

    def select_customer(self, row):
        if self.selected_customer_row:
            self.selected_customer_row.set_selected(False)

        self.selected_customer_row = row
        row.set_selected(True)

    def add_customer_to_operation(self):

        if not self.selected_customer_row:
            print("No customer selected")
            return

        name = self.selected_customer_row.name
        email = self.selected_customer_row.email
        id = self.selected_customer_row.id

        self.c.set_customer(name, email, id)

        self.navigator.go_back()

    def edit_customer(self):
        if not self.selected_customer_row:
            print("No customer selected")
            return
        
        name = self.selected_customer_row.name
        email = self.selected_customer_row.email
        id = self.selected_customer_row.id

        self.c.set_customer(name, email, id)

        self.navigator.go_to("customer_register_edit_menu")

    def refresh_orders(self):
        while self.orders_layout.count() > 1:
            item = self.orders_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for sale_id, customer_name, isPaid, total, date in self.c.listOrders():
            self.orders_layout.insertWidget(
                0,
                OrderLine(sale_id, customer_name, isPaid, total, date, self.on_order_clicked)
            )

    def on_order_clicked(self, order_line):
        detail_screen = self.navigator.screens["order_detail"]
        detail_screen.load_order(
            customer_name=order_line.customer_name,
            date=order_line.date,
            items= self.c.getSaleLines(order_line.sale_id),
            total=order_line.total,
            isPaid=order_line.isPaid,
            id=order_line.sale_id
        )
        self.navigator.go_to("order_detail")


class CustomerRegisterEditMenuScreen(QWidget):
    def __init__(self, navigator, c):
        super().__init__()
        self.navigator = navigator
        self.c = c

        layout = QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)

        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: #3a3a3a; border: 1px solid #555;")
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 10)
        left_layout.setSpacing(8)
        left_panel.setLayout(left_layout)

        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: #2e2e2e; border: none;")
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        form_frame.setLayout(form_layout)

        for label_text, attr in [("name", "name_input"), ("email", "email_input")]:
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: white; background-color: transparent;")
            lbl.setFixedWidth(50)
            inp = QLineEdit()
            inp.setStyleSheet("background-color: #555; color: white; border: 1px solid #666; padding: 3px;")
            inp.setFixedWidth(180)
            setattr(self, attr, inp)
            row.addWidget(lbl)
            row.addWidget(inp)
            row.addStretch()
            form_layout.addLayout(row)

        form_layout.addStretch()
        left_layout.addWidget(form_frame)

        button_frame = QFrame()
        button_frame.setStyleSheet("background-color: transparent; border: none;")
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(10, 0, 10, 0)
        button_frame.setLayout(button_layout)
        register_btn = QPushButton("register custommer")
        delete_btn = QPushButton("delete custommer")
        save_btn = QPushButton("save")
        back_btn = QPushButton("back")
        for btn in [register_btn, delete_btn, save_btn, back_btn]:
            btn.setStyleSheet(btn_style())
        button_layout.addWidget(register_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(back_btn)
        left_layout.addWidget(button_frame)

        register_btn.clicked.connect(self.on_register_clicked)
        save_btn.clicked.connect(self.on_save_clicked)
        back_btn.clicked.connect(self.on_back_clicked)
        delete_btn.clicked.connect(self.on_delete_clicked)

        self.status_lbl = QLabel("")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet("color: white; background-color: transparent;")
        left_layout.addWidget(self.status_lbl)

        layout.addWidget(left_panel, 0, 0)

        self.orders_panel, self.orders_layout = make_orders_panel_frame()
        layout.addWidget(self.orders_panel, 0, 1)

        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 1)

    def showEvent(self, event):
        self.refresh_orders()

        if self.c.selected_customer:
            name, email, id = self.c.selected_customer

            self.name_input.setText(name)
            self.email_input.setText(email)

    def on_register_clicked(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()

        if not name or not email:
                self.status_lbl.setStyleSheet("color: orange; background-color: transparent;")
                self.status_lbl.setText("Please fill in both fields.")
                return
        
        success = self.c.registerCustomer(name, email)

        if success:
            self.status_lbl.setStyleSheet("color: lightgreen; background-color: transparent;")
            self.status_lbl.setText(f"Customer '{name}' registered!")
            self.name_input.clear()
            self.email_input.clear()
        else:
            self.status_lbl.setStyleSheet("color: red; background-color: transparent;")
            self.status_lbl.setText("Registration failed. Name or email already exists.")

    def on_save_clicked(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()

        if not self.c.selected_customer:
            return

        if not name or not email:
                self.status_lbl.setStyleSheet("color: orange; background-color: transparent;")
                self.status_lbl.setText("Please fill in both fields.")
                return
        
        success = self.c.updateCustomer(name, email, self.c.selected_customer[2])

        if success:
            self.status_lbl.setStyleSheet("color: lightgreen; background-color: transparent;")
            self.status_lbl.setText(f"Customer '{name}' updated!")
            self.name_input.clear()
            self.email_input.clear()
        else:
            self.status_lbl.setStyleSheet("color: red; background-color: transparent;")
            self.status_lbl.setText("Saving failed. Verify name or email.")

    def on_back_clicked(self):
        self.name_input.clear()
        self.email_input.clear()
        self.status_lbl.clear()
        self.c.clearCustomer()

        self.navigator.go_back()

    def on_delete_clicked(self):
        if not self.c.selected_customer:
            return

        name = self.name_input.text().strip()

        reply = QMessageBox.question(
        self,
        "Confirm delete",
        "Delete this customer permanently?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )

        if reply == QMessageBox.StandardButton.Yes:
            success = self.c.deleteCustomer(self.c.selected_customer[2])

            if success:
                self.status_lbl.setStyleSheet("color: lightgreen; background-color: transparent;")
                self.status_lbl.setText(f"Customer '{name}' deleted!")
                self.name_input.clear()
                self.email_input.clear()
            else:
                self.status_lbl.setStyleSheet("color: red; background-color: transparent;")
                self.status_lbl.setText("Deleting failed, try again later.")

    def refresh_orders(self):
        while self.orders_layout.count() > 1:
            item = self.orders_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for sale_id, customer_name, isPaid, total, date in self.c.listOrders():
            self.orders_layout.insertWidget(
                0,
                OrderLine(sale_id, customer_name, isPaid, total, date, self.on_order_clicked)
            )
    
    def on_order_clicked(self, order_line):
        detail_screen = self.navigator.screens["order_detail"]
        detail_screen.load_order(
            customer_name=order_line.customer_name,
            date=order_line.date,
            items= self.c.getSaleLines(order_line.sale_id),
            total=order_line.total,
            isPaid=order_line.isPaid,
            id=order_line.sale_id
        )
        self.navigator.go_to("order_detail")

class OrderMenuScreen(QWidget):
    def __init__(self, navigator):
        super().__init__()
        self.navigator = navigator
        self.c = c

        layout = QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)

        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: #3a3a3a; border: 1px solid #555;")
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 10)
        left_layout.setSpacing(8)
        left_panel.setLayout(left_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")
        items_container = QWidget()
        items_container.setStyleSheet("background-color: #2e2e2e;")
        self.items_layout = QVBoxLayout()
        self.items_layout.setSpacing(2)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        items_container.setLayout(self.items_layout)

        totalPrice = 0
        for item in self.c.current_operation:
            self.items_layout.addWidget(ProductItemRow(item["product"].name, item["quantity"]))
            totalPrice += item["product"].price * item["quantity"]
        
        self.items_layout.addStretch()
        scroll.setWidget(items_container)
        left_layout.addWidget(scroll)

        ct_layout = QHBoxLayout()
        ct_layout.setContentsMargins(10, 0, 10, 0)
        ct_layout.setSpacing(10)
        self.customer_lbl = QLabel("no customer selected")
        self.customer_lbl.setStyleSheet("color: white; background-color: #3f4c56; border: 1px solid #666; padding: 6px;")
        self.total_lbl = QLabel(f"total: ${totalPrice}")
        self.total_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_lbl.setStyleSheet("color: white; background-color: #3f4c56; border: 1px solid #666; padding: 6px;")
        ct_layout.addWidget(self.customer_lbl)
        ct_layout.addWidget(self.total_lbl)
        left_layout.addLayout(ct_layout)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setStyleSheet("color: white; background-color: transparent;")
        left_layout.addWidget(self.result_label)

        button_frame = QFrame()
        button_frame.setStyleSheet("background-color: transparent; border: none;")
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(10, 0, 10, 0)
        button_frame.setLayout(button_layout)
        find_btn = QPushButton("find custommer")
        find_btn.clicked.connect(lambda: navigator.go_to("customer_menu"))
        pay_btn = QPushButton("pay")
        pay_btn.clicked.connect(self.on_pay_clicked)
        order_btn = QPushButton("order")
        order_btn.clicked.connect(self.on_orderBtn_clicked)
        cancel_btn = QPushButton("cancel")
        cancel_btn.clicked.connect(self.reset_order)
        for btn in [find_btn, pay_btn, order_btn, cancel_btn]:
            btn.setStyleSheet(btn_style())
        button_layout.addWidget(find_btn)
        button_layout.addWidget(pay_btn)
        button_layout.addWidget(order_btn)
        button_layout.addWidget(cancel_btn)
        left_layout.addWidget(button_frame)

        layout.addWidget(left_panel, 0, 0)

        self.orders_panel, self.orders_layout = make_orders_panel_frame()
        layout.addWidget(self.orders_panel, 0, 1)

        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 1)

    def showEvent(self, event):
        customer = self.c.selected_customer
        self.refresh()
        self.refresh_orders()

        if customer:
            name = customer[0]
            self.customer_lbl.setText(name)

    def refresh(self):
        # Clear all items except the stretch at the end
        while self.items_layout.count() > 1:
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        total = 0
        for item in self.c.current_operation:
            self.items_layout.insertWidget(self.items_layout.count() - 1, ProductItemRow(item["product"].name, item["quantity"]))
            total += item["product"].price * item["quantity"]

        self.total_lbl.setText(f"total: ${total:.2f}")
        if self.c.selected_customer:
            self.customer_lbl.setText(self.c.selected_customer[0])
        else:
            self.customer_lbl.setText("no customer selected")

    def reset_order(self):
        self.c.selected_customer = None
        self.c.clearOperation()
        self.customer_lbl.setText("No customer selected")
        self.navigator.go_to("main_menu")

    def refresh_orders(self):
        while self.orders_layout.count() > 1:
            item = self.orders_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for sale_id, customer_name, isPaid, total, date in self.c.listOrders():
            self.orders_layout.insertWidget(
                0,
                OrderLine(sale_id, customer_name, isPaid, total, date, self.on_order_clicked)
            )

    def on_order_clicked(self, order_line):
        detail_screen = self.navigator.screens["order_detail"]
        detail_screen.load_order(
            customer_name=order_line.customer_name,
            date=order_line.date,
            items= self.c.getSaleLines(order_line.sale_id),
            total=order_line.total,
            isPaid=order_line.isPaid,
            id=order_line.sale_id
        )
        self.navigator.go_to("order_detail")

    def on_orderBtn_clicked(self):
        if self.c.selected_customer:
            if not self.c.isPaid:
                reply = QMessageBox.question(
                self,
                "Proceed without payment",
                "Proceed without payment?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
                )

                if reply == QMessageBox.StandardButton.Yes:
                    amount = float(self.total_lbl.text().replace("total: $", ""))
                    success = self.c.registerOrder(self.c.selected_customer[2], False, amount)

                    if success:
                        self.result_label_label.setStyleSheet("color: lightgreen; background-color: transparent;")
                        self.result_label.setText("Order registered succesfully.")
                    else: 
                        self.result_label.setStyleSheet("color: orange; background-color: transparent;")
                        self.result_label.setText("Could not register the order, please try again later.")


            else:
                amount = float(self.total_lbl.text().replace("total: $", ""))
                success = self.c.registerOrder(self.c.selected_customer[2], True, amount)

                if success:
                    self.result_label.setStyleSheet("color: lightgreen; background-color: transparent;")
                    self.result_label.setText("Order registered succesfully.")
                else: 
                    self.result_label.setStyleSheet("color: orange; background-color: transparent;")
                    self.result_label.setText("Could not register the order, please try again later.")

        else:
            self.result_label.setStyleSheet("color: orange; background-color: transparent;")
            self.result_label.setText("Select a customer first.")

    def on_pay_clicked(self):
        total = sum(item["product"].price * item["quantity"] for item in self.c.current_operation)
        payment_screen = self.navigator.screens["payment_menu"]
        payment_screen.load_payment(total=total, return_screen="order_menu")
        self.navigator.go_to("payment_menu")

class OrderDetailScreen(QWidget):
    def __init__(self, navigator, c):
        super().__init__()
        self.navigator = navigator
        self.c = c

        layout = QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)

        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: #3a3a3a; border: 1px solid #555;")
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 10)
        left_layout.setSpacing(8)
        left_panel.setLayout(left_layout)

        # Header bar with customer name and date
        header_bar = QFrame()
        header_bar.setStyleSheet("background-color: #4b5b66; border: none;")
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(10, 6, 10, 6)
        header_bar.setLayout(header_layout)
        self.header_customer_lbl = QLabel("customer")
        self.header_customer_lbl.setStyleSheet("color: white; background-color: transparent;")
        self.header_date_lbl = QLabel("")
        self.header_date_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.header_date_lbl.setStyleSheet("color: white; background-color: transparent;")
        header_layout.addWidget(self.header_customer_lbl)
        header_layout.addStretch()
        header_layout.addWidget(self.header_date_lbl)
        left_layout.addWidget(header_bar)

        # Scroll area for items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")
        self.items_container = QWidget()
        self.items_container.setStyleSheet("background-color: #2e2e2e;")
        self.items_layout = QVBoxLayout()
        self.items_layout.setSpacing(2)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_container.setLayout(self.items_layout)
        self.items_layout.addStretch()
        scroll.setWidget(self.items_container)
        left_layout.addWidget(scroll)

        # Total label
        self.total_lbl = QLabel("total: $0")
        self.total_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_lbl.setStyleSheet("color: white; background-color: #3f4c56; border: 1px solid #666; padding: 6px;")
        self.total_lbl.setFixedWidth(160)
        total_wrapper = QHBoxLayout()
        total_wrapper.addStretch()
        total_wrapper.addWidget(self.total_lbl)
        total_wrapper.addStretch()
        left_layout.addLayout(total_wrapper)

        self.payment_lbl = QLabel("paid:")
        self.payment_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.payment_lbl.setStyleSheet("color: white; background-color: #3f4c56; border: 1px solid #666; padding: 6px;")
        self.payment_lbl.setFixedWidth(160)
        payment_wrapper = QHBoxLayout()
        payment_wrapper.addStretch()
        payment_wrapper.addWidget(self.payment_lbl)
        payment_wrapper.addStretch()
        left_layout.addLayout(payment_wrapper)

        # Bottom buttons
        button_frame = QFrame()
        button_frame.setStyleSheet("background-color: transparent; border: none;")
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(10, 0, 10, 0)
        button_frame.setLayout(button_layout)
        pay_btn = QPushButton("pay")
        pay_btn.clicked.connect(self.on_pay_clicked)
        collect_btn = QPushButton("collect order")
        collect_btn.clicked.connect(self.on_collect_clicked)
        back_btn = QPushButton("back")
        back_btn.clicked.connect(lambda: navigator.go_back())
        for btn in [pay_btn, collect_btn, back_btn]:
            btn.setStyleSheet(btn_style())
        button_layout.addWidget(pay_btn)
        button_layout.addWidget(collect_btn)
        button_layout.addWidget(back_btn)
        left_layout.addWidget(button_frame)

        layout.addWidget(left_panel, 0, 0)

        self.orders_panel, self.orders_layout = make_orders_panel_frame()
        layout.addWidget(self.orders_panel, 0, 1)

        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 1)

        self.refresh_orders()

    def load_order(self, customer_name, date, items, total, isPaid, id):
        """Call this before navigating here to populate the screen."""
        self.c.isPaid = isPaid
        self.c.currentOrderId = id
        self.header_customer_lbl.setText(customer_name)
        self.header_date_lbl.setText(str(date))
        self.total_lbl.setText(f"total: ${total:.2f}")
        self.payment_lbl.setStyleSheet("color: white; background-color: #3f4c56; border: 1px solid #666; padding: 6px;")
        if isPaid: self.payment_lbl.setText("paid: yes")
        else: self.payment_lbl.setText("paid: no")

        # Rebuild items list
        while self.items_layout.count() > 1:
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for name, qty in items:
            self.items_layout.insertWidget(
                self.items_layout.count() - 1,
                ProductItemRow(name, qty)
            )

    def refresh_orders(self):
        while self.orders_layout.count() > 1:
            item = self.orders_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for sale_id, customer_name, isPaid, total, date in self.c.listOrders():
            self.orders_layout.insertWidget(
                0,
                OrderLine(sale_id, customer_name, isPaid, total, date, self.on_order_clicked)
            )
    
    def on_order_clicked(self, order_line):
        detail_screen = self.navigator.screens["order_detail"]
        detail_screen.load_order(
            customer_name=order_line.customer_name,
            date=order_line.date,
            items= self.c.getSaleLines(order_line.sale_id),
            total=order_line.total,
            isPaid=order_line.isPaid,
            id=order_line.sale_id
        )
        self.navigator.go_to("order_detail")

    def on_pay_clicked(self):
        if not self.c.isPaid:
            payment_screen = self.navigator.screens["payment_menu"]
            payment_screen.load_payment(total=float(self.total_lbl.text().replace("total: $", "")), return_screen="order_menu", sale_id=self.c.currentOrderId)
            self.navigator.go_to("payment_menu")
        else:
            self.payment_lbl.setText("This order is already paid.")
            self.payment_lbl.setStyleSheet("color: orange; background-color: transparent;")

    def on_collect_clicked(self):
        if not self.c.isPaid:
            self.payment_lbl.setText("The customer needs to pay first.")
            self.payment_lbl.setStyleSheet("color: orange; background-color: transparent;")
        else:
            success = self.c.completeOrder(self.c.currentOrderId)

            if success:
                self.payment_lbl.setText("Order completed.")
                self.payment_lbl.setStyleSheet("color: green; background-color: transparent;")
            else:
                self.payment_lbl.setText("There has been an issue, please try again.")
                self.payment_lbl.setStyleSheet("color: orange; background-color: transparent;")

class PaymentMenuScreen(QWidget):
    def __init__(self, navigator, c):
        super().__init__()
        self.navigator = navigator
        self.c = c
        self.total = 0
        self.sale_id = None
        self.isSale = False

        layout = QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)

        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: #3a3a3a; border: 1px solid #555;")
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 10)
        left_layout.setSpacing(8)
        left_panel.setLayout(left_layout)

        # Form area
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: #2e2e2e; border: none;")
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        form_frame.setLayout(form_layout)

        # Amount due label
        self.amount_due_lbl = QLabel("amount due: $0.00")
        self.amount_due_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.amount_due_lbl.setStyleSheet("""
            color: white;
            background-color: #3f4c56;
            border: 1px solid #666;
            padding: 8px;
            font-size: 14px;
        """)
        form_layout.addWidget(self.amount_due_lbl)

        # Cash row
        cash_row = QHBoxLayout()
        cash_lbl = QLabel("cash")
        cash_lbl.setStyleSheet("color: white; background-color: transparent;")
        cash_lbl.setFixedWidth(80)
        self.cash_input = QLineEdit()
        self.cash_input.setPlaceholderText("0.00")
        self.cash_input.setStyleSheet("background-color: #555; color: white; border: 1px solid #666; padding: 3px;")
        self.cash_input.setFixedWidth(180)
        self.cash_input.textChanged.connect(self.on_amount_changed)
        cash_row.addWidget(cash_lbl)
        cash_row.addWidget(self.cash_input)
        cash_row.addStretch()
        form_layout.addLayout(cash_row)

        # Payconiq row
        payconiq_row = QHBoxLayout()
        payconiq_lbl = QLabel("payconiq")
        payconiq_lbl.setStyleSheet("color: white; background-color: transparent;")
        payconiq_lbl.setFixedWidth(80)
        self.payconiq_input = QLineEdit()
        self.payconiq_input.setPlaceholderText("0.00")
        self.payconiq_input.setStyleSheet("background-color: #555; color: white; border: 1px solid #666; padding: 3px;")
        self.payconiq_input.setFixedWidth(180)
        self.payconiq_input.textChanged.connect(self.on_amount_changed)
        payconiq_row.addWidget(payconiq_lbl)
        payconiq_row.addWidget(self.payconiq_input)
        payconiq_row.addStretch()
        form_layout.addLayout(payconiq_row)

        # Remaining label
        self.remaining_lbl = QLabel("remaining: $0.00")
        self.remaining_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.remaining_lbl.setStyleSheet("color: white; background-color: transparent; padding: 4px;")
        form_layout.addWidget(self.remaining_lbl)

        form_layout.addStretch()
        left_layout.addWidget(form_frame, 1)

        # Bottom buttons
        button_frame = QFrame()
        button_frame.setStyleSheet("background-color: transparent; border: none;")
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(10, 0, 10, 0)
        button_frame.setLayout(button_layout)

        register_btn = QPushButton("register payment")
        back_btn = QPushButton("back")
        back_btn.clicked.connect(lambda: navigator.go_back())
        register_btn.clicked.connect(self.on_register_clicked)
        for btn in [register_btn, back_btn]:
            btn.setStyleSheet(btn_style())
        button_layout.addWidget(register_btn)
        button_layout.addWidget(back_btn)
        left_layout.addWidget(button_frame)

        self.status_lbl = QLabel("")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet("color: white; background-color: transparent;")
        left_layout.addWidget(self.status_lbl)

        layout.addWidget(left_panel, 0, 0)

        self.orders_panel, self.orders_layout = make_orders_panel_frame()
        layout.addWidget(self.orders_panel, 0, 1)

        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 1)

        self.refresh_orders()

    def showEvent(self, event):
        self.refresh_orders()

    def load_payment(self, total, return_screen, sale_id=None, isSale=False):
        """Call before navigating here. return_screen is the screen name to go back to."""
        if isSale: self.isSale = True
        self.total = total
        if sale_id: self.sale_id = sale_id
        self.return_screen = return_screen
        self.amount_due_lbl.setText(f"amount due: ${total:.2f}")
        self.cash_input.clear()
        self.payconiq_input.clear()
        self.remaining_lbl.setText(f"remaining: ${total:.2f}")
        self.remaining_lbl.setStyleSheet("color: white; background-color: transparent; padding: 4px;")
        self.status_lbl.setText("")

    def on_amount_changed(self):
        try:
            cash = float(self.cash_input.text()) if self.cash_input.text() else 0.0
        except ValueError:
            cash = 0.0
        try:
            payconiq = float(self.payconiq_input.text()) if self.payconiq_input.text() else 0.0
        except ValueError:
            payconiq = 0.0

        remaining = self.total - cash - payconiq

        self.remaining_lbl.setText(f"remaining: ${remaining:.2f}")
        if remaining <= 0:
            self.remaining_lbl.setStyleSheet("color: lightgreen; background-color: transparent; padding: 4px;")
        else:
            self.remaining_lbl.setStyleSheet("color: orange; background-color: transparent; padding: 4px;")

    def on_register_clicked(self):
        try:
            cash = float(self.cash_input.text()) if self.cash_input.text() else 0.0
        except ValueError:
            self.status_lbl.setStyleSheet("color: red; background-color: transparent;")
            self.status_lbl.setText("Invalid cash amount.")
            return
        try:
            payconiq = float(self.payconiq_input.text()) if self.payconiq_input.text() else 0.0
        except ValueError:
            self.status_lbl.setStyleSheet("color: red; background-color: transparent;")
            self.status_lbl.setText("Invalid payconiq amount.")
            return

        if cash + payconiq < self.total:
            self.status_lbl.setStyleSheet("color: red; background-color: transparent;")
            self.status_lbl.setText(f"Amount is insufficient. Still missing: ${self.total - cash - payconiq:.2f}")
            return

        if self.isSale: success = self.c.registerSale(self.total, self.c.selected_customer[2])
        elif self.sale_id == None: success = self.c.setPaid()
        else: success = self.c.updatePaymentStatus(self.sale_id)

        if success:
            self.status_lbl.setStyleSheet("color: lightgreen; background-color: transparent;")
            self.status_lbl.setText("Payment registered!")
            self.isSale = False
            self.sale_id = None
        else:
            self.status_lbl.setStyleSheet("color: red; background-color: transparent;")
            self.status_lbl.setText("Payment failed.")

    def refresh_orders(self):
        while self.orders_layout.count() > 1:
            item = self.orders_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for sale_id, customer_name, isPaid, total, date in self.c.listOrders():
            self.orders_layout.insertWidget(
                0,
                OrderLine(sale_id, customer_name, isPaid, total, date, self.on_order_clicked)
            )

    def on_order_clicked(self, order_line):
        detail_screen = self.navigator.screens["order_detail"]
        detail_screen.load_order(
            customer_name=order_line.customer_name,
            date=order_line.date,
            items= self.c.getSaleLines(order_line.sale_id),
            total=order_line.total,
            isPaid=order_line.isPaid,
            id=order_line.sale_id
        )
        self.navigator.go_to("order_detail")

class ProductMenuScreen(QWidget):
    def __init__(self, navigator, c):
        super().__init__()
        self.navigator = navigator
        self.c = c

        layout = QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)

        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: #3a3a3a; border: 1px solid #555;")
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 10)
        left_layout.setSpacing(8)
        left_panel.setLayout(left_layout)

        list_frame = QFrame()
        list_frame.setStyleSheet("background-color: #2e2e2e; border: none;")
        list_layout = QVBoxLayout()
        list_layout.setContentsMargins(8, 8, 8, 8)
        list_layout.setSpacing(5)
        list_frame.setLayout(list_layout)

        search_input = QLineEdit()
        search_input.setPlaceholderText("search")
        search_input.setStyleSheet("background-color: #4a4a4a; color: white; border: 1px solid #666; padding: 5px;")
        search_input.textChanged.connect(self.on_search)
        list_layout.addWidget(search_input)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")
        products_container = QWidget()
        products_container.setStyleSheet("background-color: transparent;")
        self.products_layout = QVBoxLayout()
        self.products_layout.setSpacing(3)
        self.products_layout.setContentsMargins(0, 0, 0, 0)
        products_container.setLayout(self.products_layout)
        self.products_layout.addStretch()
        scroll.setWidget(products_container)
        list_layout.addWidget(scroll)
        left_layout.addWidget(list_frame, 1)

        button_frame = QFrame()
        button_frame.setStyleSheet("background-color: transparent; border: none;")
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(10, 0, 10, 0)
        button_frame.setLayout(button_layout)

        register_btn = QPushButton("new product")
        register_btn.clicked.connect(self.on_new_clicked)
        edit_btn = QPushButton("edit")
        edit_btn.clicked.connect(self.on_edit_clicked)
        delete_btn = QPushButton("delete")
        delete_btn.clicked.connect(self.on_delete_clicked)
        back_btn = QPushButton("back")
        back_btn.clicked.connect(lambda: navigator.go_back())
        for btn in [register_btn, edit_btn, delete_btn, back_btn]:
            btn.setStyleSheet(btn_style())
        button_layout.addWidget(register_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(back_btn)
        left_layout.addWidget(button_frame)

        layout.addWidget(left_panel, 0, 0)

        self.orders_panel, self.orders_layout = make_orders_panel_frame()
        layout.addWidget(self.orders_panel, 0, 1)

        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 1)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_products()
        self.refresh_orders()

    def refresh_products(self, filter_text=""):
        self.c.selected_product_row = None
        while self.products_layout.count() > 1:
            item = self.products_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for name, price, stock, id in self.c.listProducts():
            if filter_text.lower() in name.lower():
                self.products_layout.insertWidget(
                    self.products_layout.count() - 1,
                    ProductManageRow(name, price, stock, id, self)
                )

    def on_search(self, text):
        self.refresh_products(filter_text=text)

    def select_product(self, row):
        if self.c.selected_product_row:
            self.c.selected_product_row.set_selected(False)
        self.c.selected_product_row = row
        row.set_selected(True)

    def on_new_clicked(self):
        edit_screen = self.navigator.screens["product_register_edit_menu"]
        edit_screen.load_product("", "", "")
        self.navigator.go_to("product_register_edit_menu")

    def on_edit_clicked(self):
        if not self.c.selected_product_row:
            return
        edit_screen = self.navigator.screens["product_register_edit_menu"]
        edit_screen.load_product(
            self.c.selected_product_row.name,
            self.c.selected_product_row.price,
            self.c.selected_product_row.stock
        )
        self.navigator.go_to("product_register_edit_menu")

    def on_delete_clicked(self):
        if not self.c.selected_product_row:
            return
        
        reply = QMessageBox.question(
        self,
        "Confirm delete",
        "Delete this product permanently?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )

        if reply == QMessageBox.StandardButton.Yes:
            success = self.c.deleteProduct()
            if success:
                self.refresh_products()

    def refresh_orders(self):
        while self.orders_layout.count() > 1:
            item = self.orders_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for sale_id, customer_name, isPaid, total, date in self.c.listOrders():
            self.orders_layout.insertWidget(
                0,
                OrderLine(sale_id, customer_name, isPaid, total, date, self.on_order_clicked)
            )

    def on_order_clicked(self, order_line):
        detail_screen = self.navigator.screens["order_detail"]
        detail_screen.load_order(
            customer_name=order_line.customer_name,
            date=order_line.date,
            items= self.c.getSaleLines(order_line.sale_id),
            total=order_line.total,
            isPaid=order_line.isPaid,
            id=order_line.sale_id
        )
        self.navigator.go_to("order_detail")


class ProductRegisterEditMenuScreen(QWidget):
    def __init__(self, navigator, c):
        super().__init__()
        self.navigator = navigator
        self.c = c
        self.original_name = None

        layout = QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)

        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: #3a3a3a; border: 1px solid #555;")
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 10)
        left_layout.setSpacing(8)
        left_panel.setLayout(left_layout)

        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: #2e2e2e; border: none;")
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        form_frame.setLayout(form_layout)

        for label_text, attr in [("name", "name_input"), ("price", "price_input"), ("stock", "stock_input")]:
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: white; background-color: transparent;")
            lbl.setFixedWidth(50)
            inp = QLineEdit()
            inp.setStyleSheet("background-color: #555; color: white; border: 1px solid #666; padding: 3px;")
            inp.setFixedWidth(180)
            setattr(self, attr, inp)
            row.addWidget(lbl)
            row.addWidget(inp)
            row.addStretch()
            form_layout.addLayout(row)

        form_layout.addStretch()
        left_layout.addWidget(form_frame, 1)

        button_frame = QFrame()
        button_frame.setStyleSheet("background-color: transparent; border: none;")
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(10, 0, 10, 0)
        button_frame.setLayout(button_layout)

        save_btn = QPushButton("save")
        register_btn = QPushButton("register product")
        back_btn = QPushButton("back")
        back_btn.clicked.connect(lambda: navigator.go_back())
        save_btn.clicked.connect(self.on_save_clicked)
        register_btn.clicked.connect(self.on_register_clicked)
        for btn in [register_btn, save_btn, back_btn]:
            btn.setStyleSheet(btn_style())
        button_layout.addWidget(register_btn)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(back_btn)
        left_layout.addWidget(button_frame)

        self.status_lbl = QLabel("")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet("color: white; background-color: transparent;")
        left_layout.addWidget(self.status_lbl)

        layout.addWidget(left_panel, 0, 0)

        self.orders_panel, self.orders_layout = make_orders_panel_frame()
        layout.addWidget(self.orders_panel, 0, 1)

        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 1)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_orders()

    def load_product(self, name, price, stock):
        self.original_name = name if name else None
        self.name_input.setText(str(name))
        self.price_input.setText(str(price))
        self.stock_input.setText(str(stock))
        self.status_lbl.setText("")

    def on_register_clicked(self):
        name = self.name_input.text().strip()
        price = self.price_input.text().strip()
        stock = self.stock_input.text().strip()

        if not name or not price or not stock:
            self.status_lbl.setStyleSheet("color: orange; background-color: transparent;")
            self.status_lbl.setText("Please fill in all fields.")
            return

        try:
            price = float(price)
            stock = int(stock)
        except ValueError:
            self.status_lbl.setStyleSheet("color: red; background-color: transparent;")
            self.status_lbl.setText("Price must be a number, stock must be a whole number.")
            return

        success = self.c.registerProduct(name, price, stock)
        if success:
            self.status_lbl.setStyleSheet("color: lightgreen; background-color: transparent;")
            self.status_lbl.setText(f"Product '{name}' registered!")
            self.name_input.clear()
            self.price_input.clear()
            self.stock_input.clear()
        else:
            self.status_lbl.setStyleSheet("color: red; background-color: transparent;")
            self.status_lbl.setText("Registration failed. Product already exists.")

    def on_save_clicked(self):
        name = self.name_input.text().strip()
        price = self.price_input.text().strip()
        stock = self.stock_input.text().strip()

        if not name or not price or not stock:
            self.status_lbl.setStyleSheet("color: orange; background-color: transparent;")
            self.status_lbl.setText("Please fill in all fields.")
            return

        if not self.original_name:
            self.status_lbl.setStyleSheet("color: orange; background-color: transparent;")
            self.status_lbl.setText("No product loaded for editing.")
            return

        try:
            price = float(price)
            stock = int(stock)
        except ValueError:
            self.status_lbl.setStyleSheet("color: red; background-color: transparent;")
            self.status_lbl.setText("Price must be a number, stock must be a whole number.")
            return

        success = self.c.updateProduct(name, price, stock)
        if success:
            self.status_lbl.setStyleSheet("color: lightgreen; background-color: transparent;")
            self.status_lbl.setText("Product updated!")
            self.original_name = name
        else:
            self.status_lbl.setStyleSheet("color: red; background-color: transparent;")
            self.status_lbl.setText("Update failed. Name already exists.")

    def refresh_orders(self):
        while self.orders_layout.count() > 1:
            item = self.orders_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for sale_id, customer_name, isPaid, total, date in self.c.listOrders():
            self.orders_layout.insertWidget(
                0,
                OrderLine(sale_id, customer_name, isPaid, total, date, self.on_order_clicked)
            )

    def on_order_clicked(self, order_line):
        detail_screen = self.navigator.screens["order_detail"]
        detail_screen.load_order(
            customer_name=order_line.customer_name,
            date=order_line.date,
            items= self.c.getSaleLines(order_line.sale_id),
            total=order_line.total,
            isPaid=order_line.isPaid,
            id=order_line.sale_id
        )
        self.navigator.go_to("order_detail")


# ── Reusable row widgets ──────────────────────────────────────────────────────

class ProductRow(QFrame):
    def __init__(self, name, price, stock):
        super().__init__()
        self.c = c
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
        QFrame { background-color: #5b6b78; border-radius: 8px; }
        QLabel { color: white; background-color: transparent; }
        QPushButton { background-color: #3f4c56; color: white; border-radius: 4px; }
        """)
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)
        name_lbl = QLabel(name)
        avail_lbl = QLabel(str(stock))
        price_lbl = QLabel(price)
        qty = QSpinBox()
        qty.setMinimum(1)
        qty.setMaximum(99)
        qty.setFixedWidth(70)
        qty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qty.setStyleSheet("QSpinBox { padding-right: 20px; } QSpinBox::up-button { width: 16px; } QSpinBox::down-button { width: 16px; }")
        add_btn = QPushButton("Add")
        add_btn.setFixedWidth(60)
        add_btn.clicked.connect(lambda: self.c.addToOperation(model.Product(self.c.getProductId(name), name, float(price), int(stock)), qty.value()))
        layout.addWidget(name_lbl, 3)
        layout.addWidget(avail_lbl, 1)
        layout.addWidget(price_lbl, 1)
        layout.addWidget(qty, 1)
        layout.addWidget(add_btn, 1)
        self.setLayout(layout)

class ProductManageRow(QFrame):
    def __init__(self, name, price, stock, id, parent_screen):
        super().__init__()
        self.name = name
        self.price = price
        self.stock = stock
        self.product_id = id
        self.selected = False
        self.parent_screen = parent_screen
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.update_style()
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)
        name_lbl = QLabel(name)
        price_lbl = QLabel(f"${price}")
        price_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stock_lbl = QLabel(f"stock: {stock}")
        stock_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        for lbl in [name_lbl, price_lbl, stock_lbl]:
            lbl.setStyleSheet("color: white; background-color: transparent;")
        layout.addWidget(name_lbl, 3)
        layout.addWidget(price_lbl, 1)
        layout.addWidget(stock_lbl, 1)
        self.setLayout(layout)

    def mousePressEvent(self, event):
        self.parent_screen.select_product(self)

    def set_selected(self, value):
        self.selected = value
        self.update_style()

    def update_style(self):
        if self.selected:
            self.setStyleSheet("QFrame { background-color: #3a7bd5; border-radius: 2px; } QLabel { color: white; background: transparent; }")
        else:
            self.setStyleSheet("QFrame { background-color: #4a4a4a; border-radius: 2px; } QLabel { color: white; background: transparent; } QFrame:hover { background-color: #5a5a5a; }")


class ProductItemRow(QFrame):
    def __init__(self, name, quantity):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("QFrame { background-color: transparent; } QLabel { color: white; background-color: transparent; }")
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        name_lbl = QLabel(name)
        qty_lbl = QLabel(f"{quantity}X")
        qty_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(name_lbl, 3)
        layout.addWidget(qty_lbl, 1)
        self.setLayout(layout)


class CustomerRow(QFrame):
    clicked = pyqtSignal(str, str)

    def __init__(self, name, email, id, parent_screen):
        super().__init__()
        self.name = name
        self.email = email
        self.id = id
        self.selected = False
        self.parent_screen = parent_screen

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.update_style()

        self.setStyleSheet("QFrame { background-color: #4a4a4a; border-radius: 2px; } QLabel { color: white; background-color: transparent; }")
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)
        name_lbl = QLabel(name)
        email_lbl = QLabel(email)
        email_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(name_lbl, 1)
        layout.addWidget(email_lbl, 1)
        self.setLayout(layout)

    def mousePressEvent(self, event):
        self.parent_screen.select_customer(self)

    def set_selected(self, value):
        self.selected = value
        self.update_style()

    def update_style(self):

        if self.selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #3a7bd5;
                    border-radius: 2px;
                }
                QLabel {
                    color: white;
                    background: transparent;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #4a4a4a;
                    border-radius: 2px;
                }
                QLabel {
                    color: white;
                    background: transparent;
                }
                QFrame:hover {
                    background-color: #5a5a5a;
                }
            """)


# ── Navigator + MainWindow ────────────────────────────────────────────────────

class Navigator:
    """Wraps the QStackedWidget and keeps a history stack for go_back()."""
    def __init__(self, stack: QStackedWidget):
        self.stack = stack
        self.history = []
        self.screens = {}

    def register(self, name: str, widget: QWidget):
        self.screens[name] = widget

    def go_to(self, name: str):
        widget = self.screens.get(name)
        if widget is None:
            print(f"[Navigator] unknown screen: '{name}'")
            return
        self.history.append(self.stack.currentIndex())
        self.stack.setCurrentWidget(widget)

    def go_back(self):
        if self.history:
            self.stack.setCurrentIndex(self.history.pop())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        self.resize(800, 500)
        self.setStyleSheet("background-color: #2b2b2b;")

        stack = QStackedWidget()
        navigator = Navigator(stack)

        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, make_toolbar(self, navigator))

        screens = {
            "main_menu":                    MainMenuScreen(navigator),
            "sale_menu":                    SaleMenuScreen(navigator),
            "customer_menu":                CustomerMenuScreen(navigator),
            "customer_register_edit_menu":  CustomerRegisterEditMenuScreen(navigator, c),
            "order_menu":                   OrderMenuScreen(navigator),
            "order_detail":                 OrderDetailScreen(navigator, c),
            "payment_menu":                 PaymentMenuScreen(navigator, c),
            "product_menu":                 ProductMenuScreen(navigator, c),
            "product_register_edit_menu":   ProductRegisterEditMenuScreen(navigator, c),
        }

        for name, screen in screens.items():
            navigator.register(name, screen)
            stack.addWidget(screen)

        stack.setCurrentWidget(screens["main_menu"])
        self.setCentralWidget(stack)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
