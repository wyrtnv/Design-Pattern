"""
Repository pattern — Data Access Layer.

Every SQL statement of the application lives in this file. Services call
methods such as products.get(5) or orders.create(...) and receive model
objects; they never see SQL, connections or sqlite3.Row.

Security: every query is parameterized (`?` placeholders). User input is never
concatenated into SQL text, which prevents SQL injection.
"""

from models.entities import (
    Category,
    Notification,
    Order,
    OrderItem,
    Payment,
    Product,
    User,
)
from patterns.singleton_database import Database


class BaseRepository:
    def __init__(self, db: Database = None):
        self._db = db

    @property
    def db(self) -> Database:
        # Resolved lazily: repositories created at import time still use the
        # Database singleton that exists when the query actually runs.
        return self._db or Database()


# --------------------------------------------------------------------------
class UserRepository(BaseRepository):
    @staticmethod
    def _to_model(row):
        return User(row["id"], row["username"], row["full_name"], row["role"], row["password_hash"])

    def get(self, user_id):
        with self.db.transaction() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return self._to_model(row) if row else None

    def get_by_username(self, username):
        with self.db.transaction() as conn:
            row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        return self._to_model(row) if row else None

    def create(self, username, password_hash, full_name, role="customer"):
        with self.db.transaction() as conn:
            cur = conn.execute(
                "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                (username, password_hash, full_name, role),
            )
            return cur.lastrowid

    def count(self):
        with self.db.transaction() as conn:
            return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]


# --------------------------------------------------------------------------
class CategoryRepository(BaseRepository):
    def get_all(self):
        with self.db.transaction() as conn:
            rows = conn.execute(
                """SELECT c.id, c.name, COUNT(p.id) AS product_count
                   FROM categories c LEFT JOIN products p ON p.category_id = c.id
                   GROUP BY c.id ORDER BY c.name"""
            ).fetchall()
        return [Category(r["id"], r["name"], r["product_count"]) for r in rows]

    def get(self, category_id):
        with self.db.transaction() as conn:
            row = conn.execute("SELECT id, name FROM categories WHERE id = ?", (category_id,)).fetchone()
        return Category(row["id"], row["name"]) if row else None

    def create(self, name):
        with self.db.transaction() as conn:
            return conn.execute("INSERT INTO categories (name) VALUES (?)", (name,)).lastrowid

    def update(self, category_id, name):
        with self.db.transaction() as conn:
            conn.execute("UPDATE categories SET name = ? WHERE id = ?", (name, category_id))

    def delete(self, category_id):
        with self.db.transaction() as conn:
            conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))


# --------------------------------------------------------------------------
class ProductRepository(BaseRepository):
    _SELECT = """SELECT p.*, c.name AS category_name
                 FROM products p JOIN categories c ON c.id = p.category_id"""
    _SORTS = {
        "price_asc": "p.price ASC",
        "price_desc": "p.price DESC",
        "name": "p.name COLLATE NOCASE ASC",
        "new": "p.id DESC",
    }

    @staticmethod
    def _to_model(row):
        return Product(row["id"], row["category_id"], row["name"], row["description"],
                       row["price"], row["stock"], row["icon"], row["category_name"])

    def search(self, text="", category_id=None, sort="new"):
        conditions, params = [], []
        if text:
            conditions.append("(p.name LIKE ? OR p.description LIKE ?)")
            params += [f"%{text}%", f"%{text}%"]
        if category_id:
            conditions.append("p.category_id = ?")
            params.append(category_id)
        where = (" WHERE " + " AND ".join(conditions)) if conditions else ""
        order_by = self._SORTS.get(sort, self._SORTS["new"])   # whitelist, never user text
        with self.db.transaction() as conn:
            rows = conn.execute(f"{self._SELECT}{where} ORDER BY {order_by}", params).fetchall()
        return [self._to_model(r) for r in rows]

    def get(self, product_id):
        with self.db.transaction() as conn:
            row = conn.execute(f"{self._SELECT} WHERE p.id = ?", (product_id,)).fetchone()
        return self._to_model(row) if row else None

    def create(self, category_id, name, description, price, stock, icon):
        with self.db.transaction() as conn:
            return conn.execute(
                """INSERT INTO products (category_id, name, description, price, stock, icon)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (category_id, name, description, price, stock, icon),
            ).lastrowid

    def update(self, product_id, category_id, name, description, price, stock, icon):
        with self.db.transaction() as conn:
            conn.execute(
                """UPDATE products SET category_id = ?, name = ?, description = ?,
                       price = ?, stock = ?, icon = ? WHERE id = ?""",
                (category_id, name, description, price, stock, icon, product_id),
            )

    def delete(self, product_id):
        with self.db.transaction() as conn:
            conn.execute("DELETE FROM products WHERE id = ?", (product_id,))

    def change_stock(self, product_id, delta):
        with self.db.transaction() as conn:
            conn.execute("UPDATE products SET stock = MAX(stock + ?, 0) WHERE id = ?", (delta, product_id))


# --------------------------------------------------------------------------
class OrderRepository(BaseRepository):
    @staticmethod
    def _to_model(row):
        return Order(row["id"], row["user_id"], row["status"], row["delivery_method"],
                     row["delivery_cost"], row["subtotal"], row["total"], row["address"],
                     row["created_at"], row["customer_name"])

    def _load_details(self, conn, order):
        items = conn.execute(
            """SELECT oi.*, p.name AS product_name, p.icon
               FROM order_items oi JOIN products p ON p.id = oi.product_id
               WHERE oi.order_id = ?""",
            (order.id,),
        ).fetchall()
        order.items = [OrderItem(i["product_id"], i["quantity"], i["unit_price"],
                                 i["product_name"], i["icon"]) for i in items]
        pay = conn.execute("SELECT * FROM payments WHERE order_id = ? ORDER BY id DESC LIMIT 1",
                           (order.id,)).fetchone()
        if pay:
            order.payment = Payment(pay["id"], pay["order_id"], pay["method"], pay["amount"],
                                    pay["fee"], pay["transaction_id"], pay["status"], pay["created_at"])
        return order

    _SELECT = """SELECT o.*, u.full_name AS customer_name
                 FROM orders o JOIN users u ON u.id = o.user_id"""

    def create(self, user_id, delivery_method, delivery_cost, subtotal, total, address, items):
        """Order + all its items in ONE transaction: either everything is saved or nothing."""
        with self.db.transaction() as conn:
            order_id = conn.execute(
                """INSERT INTO orders (user_id, delivery_method, delivery_cost, subtotal, total, address)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, delivery_method, delivery_cost, subtotal, total, address),
            ).lastrowid
            conn.executemany(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                [(order_id, i.product_id, i.quantity, i.unit_price) for i in items],
            )
        return order_id

    def get(self, order_id):
        with self.db.transaction() as conn:
            row = conn.execute(f"{self._SELECT} WHERE o.id = ?", (order_id,)).fetchone()
            return self._load_details(conn, self._to_model(row)) if row else None

    def get_for_user(self, user_id):
        with self.db.transaction() as conn:
            rows = conn.execute(f"{self._SELECT} WHERE o.user_id = ? ORDER BY o.id DESC", (user_id,)).fetchall()
            return [self._load_details(conn, self._to_model(r)) for r in rows]

    def get_all(self, status=None):
        with self.db.transaction() as conn:
            if status:
                rows = conn.execute(f"{self._SELECT} WHERE o.status = ? ORDER BY o.id DESC", (status,)).fetchall()
            else:
                rows = conn.execute(f"{self._SELECT} ORDER BY o.id DESC").fetchall()
            return [self._load_details(conn, self._to_model(r)) for r in rows]

    def set_status(self, order_id, status):
        with self.db.transaction() as conn:
            conn.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))

    def delete(self, order_id):
        with self.db.transaction() as conn:
            conn.execute("DELETE FROM orders WHERE id = ?", (order_id,))

    def stats(self):
        with self.db.transaction() as conn:
            row = conn.execute(
                """SELECT COUNT(*) AS orders,
                          COALESCE(SUM(CASE WHEN status != 'CANCELLED' THEN total END), 0) AS revenue
                   FROM orders"""
            ).fetchone()
        return {"orders": row["orders"], "revenue": row["revenue"]}


# --------------------------------------------------------------------------
class PaymentRepository(BaseRepository):
    def create(self, order_id, method, amount, fee, transaction_id, status="SUCCESS"):
        with self.db.transaction() as conn:
            return conn.execute(
                """INSERT INTO payments (order_id, method, amount, fee, transaction_id, status)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (order_id, method, amount, fee, transaction_id, status),
            ).lastrowid


# --------------------------------------------------------------------------
class NotificationRepository(BaseRepository):
    def add(self, user_id, order_id, message):
        with self.db.transaction() as conn:
            conn.execute("INSERT INTO notifications (user_id, order_id, message) VALUES (?, ?, ?)",
                         (user_id, order_id, message))

    def for_user(self, user_id):
        with self.db.transaction() as conn:
            rows = conn.execute("SELECT * FROM notifications WHERE user_id = ? ORDER BY id DESC",
                                (user_id,)).fetchall()
        return [Notification(r["id"], r["user_id"], r["order_id"], r["message"],
                             bool(r["is_read"]), r["created_at"]) for r in rows]

    def unread_count(self, user_id):
        with self.db.transaction() as conn:
            return conn.execute("SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0",
                                (user_id,)).fetchone()[0]

    def mark_all_read(self, user_id):
        with self.db.transaction() as conn:
            conn.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
