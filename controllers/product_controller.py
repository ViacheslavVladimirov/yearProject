from PyQt6.QtWidgets import QMessageBox

class ProductController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.model.on_data_changed.append(self.update_view)

        self.view.add_requested.connect(self.on_add_requested)
        self.view.edit_requested.connect(self.on_edit_requested)
        self.view.delete_requested.connect(self.on_delete_requested)
        self.view.save_requested.connect(self.on_save_requested)
        self.view.cancel_requested.connect(self.on_cancel_requested)

        self.update_view()

    def update_view(self):
        self.view.display_products(self.model.get_all())

    def on_add_requested(self):
        self.current_edit_index = -1
        self.view.show_form()

    def on_edit_requested(self, index):
        self.current_edit_index = index
        product_data = self.model.get_all()[index]
        self.view.show_form(product_data)

    def on_delete_requested(self, index):
        reply = QMessageBox.question(
            self.view, 'Delete Product',
            'Are you sure you want to delete this product?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.model.delete(index)

    def on_save_requested(self, data):
        if self.current_edit_index == -1:
            self.model.add(data)
        else:
            self.model.update(self.current_edit_index, data)
        self.view.show_table()

    def on_cancel_requested(self):
        self.view.show_table()
