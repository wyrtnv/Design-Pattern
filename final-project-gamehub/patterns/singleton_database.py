"""
Pattern 2 — Singleton (Creational).

Database is the single shared access point to SQLite for the whole application.
Every repository asks Database() for a connection; there is always exactly one
Database object, so the path, the schema setup and the foreign-key PRAGMA are
configured in one place only.

SQLite connections must not be shared between Flask's worker threads, so the
Singleton does not keep one global connection. It hands out a fresh
connection per unit of work through the transaction() context manager, which
commits on success and rolls back on any error.
"""

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_FILE = BASE_DIR / "database" / "schema.sql"
SEED_FILE = BASE_DIR / "database" / "seed.sql"


class Database:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path=None):
        # Double-checked locking: safe even if two threads start at once.
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance.db_path = str(db_path or BASE_DIR / "gamehub.db")
                    cls._instance = instance
        return cls._instance

    # --- connections -------------------------------------------------------
    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @contextmanager
    def transaction(self):
        """One unit of work: commit if the block succeeds, otherwise roll back."""
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # --- setup -------------------------------------------------------------
    def init_schema(self):
        with self.transaction() as conn:
            conn.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))

    def seed_catalog(self):
        with self.transaction() as conn:
            conn.executescript(SEED_FILE.read_text(encoding="utf-8"))

    # --- tests only --------------------------------------------------------
    @classmethod
    def _reset_for_tests(cls):
        cls._instance = None
