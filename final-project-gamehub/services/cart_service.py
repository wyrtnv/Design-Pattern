"""
Shopping cart kept in the Flask session as {"product_id": quantity}.
The cart stores only ids and quantities; prices are always re-read from the
database, so a user cannot change a price by editing the session cookie.
"""

from models.entities import OrderItem
from repositories.repositories import ProductRepository


class CartService:
    def __init__(self, session_cart: dict, products: ProductRepository = None):
        self.cart = session_cart
        self.products = products or ProductRepository()

    def add(self, product_id, quantity=1):
        product = self.products.get(product_id)
        if product is None:
            raise LookupError("Product not found.")
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")
        new_qty = self.cart.get(str(product_id), 0) + quantity
        if new_qty > product.stock:
            raise ValueError(f"Only {product.stock} × {product.name} left in stock.")
        self.cart[str(product_id)] = new_qty
        return product

    def set_quantity(self, product_id, quantity):
        if quantity <= 0:
            self.cart.pop(str(product_id), None)
            return
        product = self.products.get(product_id)
        if product is None:
            self.cart.pop(str(product_id), None)
            return
        if quantity > product.stock:
            raise ValueError(f"Only {product.stock} × {product.name} left in stock.")
        self.cart[str(product_id)] = quantity

    def remove(self, product_id):
        self.cart.pop(str(product_id), None)

    def clear(self):
        self.cart.clear()

    def items(self):
        """[OrderItem] with current prices from the database."""
        result = []
        for pid, qty in list(self.cart.items()):
            product = self.products.get(int(pid))
            if product is None:
                self.cart.pop(pid, None)
                continue
            result.append(OrderItem(product.id, qty, product.price, product.name, product.icon))
        return result

    def count(self):
        return sum(self.cart.values())
