import os
import sqlite3

# The database file is always created next to this file,
# no matter which folder the app is started from.
DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")


def connect():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = connect()
    # discount / apply_tax / apply_shipping store which decorators
    # are selected for the product
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL CHECK(price > 0),
            category TEXT NOT NULL,
            discount INTEGER NOT NULL DEFAULT 0 CHECK(discount BETWEEN 0 AND 90),
            apply_tax INTEGER NOT NULL DEFAULT 0,
            apply_shipping INTEGER NOT NULL DEFAULT 0
        )
    """)

    count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    if count == 0:
        conn.executemany("""
            INSERT INTO products (name, price, category, discount, apply_tax, apply_shipping)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            ("iPhone 15", 450000, "Electronics", 10, 1, 1),
            ("Nike Air Max", 65000, "Clothing", 20, 1, 0),
            ("Harry Potter Book", 8000, "Books", 0, 0, 1),
            ("Coffee Machine", 120000, "Home", 5, 1, 1),
        ])

    conn.commit()
    conn.close()


# ---------------------------- CRUD ----------------------------

def get_all_products():
    conn = connect()
    rows = conn.execute("SELECT * FROM products ORDER BY id").fetchall()
    conn.close()
    return rows


def get_product(product_id):
    conn = connect()
    row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    return row


def add_product(data):
    conn = connect()
    conn.execute("""
        INSERT INTO products (name, price, category, discount, apply_tax, apply_shipping)
        VALUES (:name, :price, :category, :discount, :apply_tax, :apply_shipping)
    """, data)
    conn.commit()
    conn.close()


def update_product(product_id, data):
    conn = connect()
    conn.execute("""
        UPDATE products
        SET name = :name, price = :price, category = :category,
            discount = :discount, apply_tax = :apply_tax, apply_shipping = :apply_shipping
        WHERE id = :id
    """, {**data, "id": product_id})
    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = connect()
    conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
