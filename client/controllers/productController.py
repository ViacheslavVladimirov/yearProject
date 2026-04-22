from PyQt6.QtWidgets import QMessageBox
from .apiClient import get_all_products, create_product, update_product, delete_product
from models.product import Product

class ProductController:
    def __init__(self, view):
        self.view = view
        self.status_callback = lambda m, e=False: None

        # Connect view signals to controller actions
        self.view.add_requested.connect(self.on_add_requested)
        self.view.edit_requested.connect(self.on_edit_requested)
        self.view.delete_requested.connect(self.on_delete_requested)
        self.view.save_requested.connect(self.on_save_requested)
        self.view.cancel_requested.connect(self.on_cancel_requested)

    def update_view(self):
        raw_products = get_all_products() or []
        products = [Product.deserialize(p).serialize() for p in raw_products]
        self.view.display_products(products)

    def on_add_requested(self):
        self.current_edit_index = -1
        self.view.show_form()

    def on_edit_requested(self, index):
        self.current_edit_index = index
        raw_products = get_all_products()
        if raw_products and 0 <= index < len(raw_products):
            product_data = Product.deserialize(raw_products[index]).serialize()
            self.view.show_form(product_data)

    def on_delete_requested(self, index):
        reply = QMessageBox.question(
            self.view, 'Delete Product',
            'Are you sure you want to delete this product?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            raw_products = get_all_products()
            if raw_products and 0 <= index < len(raw_products):
                product_id = raw_products[index]['id']
                success = delete_product(product_id)
                if success:
                    self.status_callback("Product deleted successfully")
                else:
                    self.status_callback("Failed to delete product", True)
                self.update_view()

    def on_save_requested(self, data):
        product = Product.deserialize(data)
        payload = product.serialize()
        if self.current_edit_index == -1:
            success = create_product(payload)
            if success:
                self.status_callback("Product created successfully")
            else:
                self.status_callback("Failed to create product", True)
        else:
            raw_products = get_all_products()
            if raw_products and 0 <= self.current_edit_index < len(raw_products):
                product_id = raw_products[self.current_edit_index]['id']
                success = update_product(product_id, payload)
                if success:
                    self.status_callback("Product updated successfully")
                else:
                    self.status_callback("Failed to update product", True)
        self.update_view()
        self.view.show_table()

    def on_cancel_requested(self):
        self.view.show_table()
