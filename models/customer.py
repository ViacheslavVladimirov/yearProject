class Customer:
    def __init__(self, id=None, name="", email="", phone=""):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone
        }

    @staticmethod
    def deserialize(data):
        return Customer(
            id=data.get("id"),
            name=data.get("name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", "")
        )
