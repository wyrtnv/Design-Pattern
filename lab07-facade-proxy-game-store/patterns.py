import sqlite3

from database import connect


# =====================================================================
# PROXY PATTERN
# ---------------------------------------------------------------------
# ProductService  - the "real subject": it really works with the
#                   products table (CRUD).
# ProductProxy    - the "proxy": it has exactly the same methods as
#                   ProductService, but before delegating each call it
#                   checks the user's role. Customers may only view
#                   products; adding, editing and deleting is allowed
#                   only for administrators.
# Flask routes talk ONLY to the proxy, never to ProductService directly.
# =====================================================================

class ProductService:
    """Real subject: performs the actual database operations."""

    def get_all(self):
        conn = connect()
        rows = conn.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
        conn.close()
        return rows

    def get(self, product_id):
        conn = connect()
        row = conn.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchone()
        conn.close()
        return row

    def add(self, name, category, price):
        conn = connect()
        conn.execute(
            "INSERT INTO products (name, category, price) VALUES (?, ?, ?)",
            (name, category, price),
        )
        conn.commit()
        conn.close()

    def update(self, product_id, name, category, price):
        conn = connect()
        conn.execute(
            "UPDATE products SET name = ?, category = ?, price = ? WHERE id = ?",
            (name, category, price, product_id),
        )
        conn.commit()
        conn.close()

    def delete(self, product_id):
        conn = connect()
        try:
            conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.rollback()
            raise ValueError("Cannot delete a product that is used in an order.")
        finally:
            conn.close()


class ProductProxy:
    """Proxy: same interface as ProductService + access control."""

    ADMIN_ONLY_ACTIONS = {"create", "update", "delete"}

    def __init__(self, role, service=None):
        self.role = role
        self._service = service or ProductService()

    def check_permission(self, action):
        if action in self.ADMIN_ONLY_ACTIONS and self.role != "admin":
            raise PermissionError("Only administrators can manage products.")
        return True

    # --- read operations: available to everyone ---
    def get_all(self):
        self.check_permission("view")
        return self._service.get_all()

    def get(self, product_id):
        self.check_permission("view")
        return self._service.get(product_id)

    # --- write operations: administrators only ---
    def add(self, name, category, price):
        self.check_permission("create")
        return self._service.add(name, category, price)

    def update(self, product_id, name, category, price):
        self.check_permission("update")
        return self._service.update(product_id, name, category, price)

    def delete(self, product_id):
        self.check_permission("delete")
        return self._service.delete(product_id)


# =====================================================================
# FACADE PATTERN
# ---------------------------------------------------------------------
# Placing an order needs several subsystems:
#   OrderValidator   - checks the customer name and quantity
#   ProductCatalog   - finds the product in the database
#   PriceCalculator  - calculates the total price
#   OrderRepository  - saves and reads orders
# OrderFacade hides all of them behind ONE simple method: place_order().
# The Flask route calls only the facade and knows nothing about the steps.
# =====================================================================

class OrderValidator:
    def validate(self, customer_name, quantity):
        if not customer_name or not customer_name.strip():
            raise ValueError("Customer name is required.")
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")


class ProductCatalog:
    def find(self, product_id):
        conn = connect()
        product = conn.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchone()
        conn.close()
        if product is None:
            raise ValueError("Product not found.")
        return product


class PriceCalculator:
    def calculate(self, price, quantity):
        return round(price * quantity, 2)


class OrderRepository:
    BASE_QUERY = """
        SELECT orders.*, products.name AS product_name
        FROM orders
        JOIN products ON products.id = orders.product_id
    """

    def save(self, customer_name, product_id, quantity, total_price):
        conn = connect()
        try:
            conn.execute("""
                INSERT INTO orders (customer_name, product_id, quantity, total_price)
                VALUES (?, ?, ?, ?)
            """, (customer_name, product_id, quantity, total_price))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_all(self):
        conn = connect()
        rows = conn.execute(self.BASE_QUERY + " ORDER BY orders.id DESC").fetchall()
        conn.close()
        return rows

    def get_by_customer(self, customer_name):
        conn = connect()
        rows = conn.execute(
            self.BASE_QUERY + " WHERE orders.customer_name = ? ORDER BY orders.id DESC",
            (customer_name,),
        ).fetchall()
        conn.close()
        return rows


class OrderFacade:
    """Facade: one simple interface for the whole ordering process."""

    def __init__(self):
        self.validator = OrderValidator()
        self.catalog = ProductCatalog()
        self.calculator = PriceCalculator()
        self.repository = OrderRepository()

    def place_order(self, customer_name, product_id, quantity):
        # 1. validation
        self.validator.validate(customer_name, quantity)
        # 2. product lookup
        product = self.catalog.find(product_id)
        # 3. price calculation
        total = self.calculator.calculate(product["price"], quantity)
        # 4. saving the order
        self.repository.save(customer_name.strip(), product_id, quantity, total)
        return total

    def get_orders(self, username, role):
        if role == "admin":
            return self.repository.get_all()
        return self.repository.get_by_customer(username)
