import os
import sqlite3

# The database file is always created next to this file,
# no matter which folder the app is started from.
DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "store.db")


def connect():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = connect()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL CHECK(price >= 0)
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            total_price REAL NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(id)
                ON DELETE RESTRICT
        );
    """)

    count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    if count == 0:
        conn.executemany("""
            INSERT INTO products (name, category, price)
            VALUES (?, ?, ?)
        """, [
            ("Gaming Mouse", "Accessories", 35),
            ("Gaming Keyboard", "Accessories", 75),
            ("Gaming Laptop", "Computers", 1200),
            ("Gaming Headset", "Audio", 60),
        ])

    conn.commit()
    conn.close()
