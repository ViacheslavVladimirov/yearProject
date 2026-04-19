class Product:
    def __init__(self, id=None, name="", price=0.0, stock=0):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "stock": self.stock
        }

    @staticmethod
    def deserialize(data):
        return Product(
            id=data.get("id"),
            name=data.get("name", ""),
            price=data.get("price", 0.0),
            stock=data.get("stock", 0)
        )
