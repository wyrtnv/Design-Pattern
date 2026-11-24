"""
Singleton Pattern — DatabaseManager.

Only ONE DatabaseManager (and therefore one SQLAlchemy object with one
connection pool) exists in the whole application. Every call to
DatabaseManager() returns the very same object.
"""

from flask_sqlalchemy import SQLAlchemy


class DatabaseManager:
    _instance = None

    def __new__(cls, app=None):
        # Create the object only the first time
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.db = SQLAlchemy()
            cls._instance._initialized_app = None

        # Note: in the lab template this check was inside the "if" above,
        # so DatabaseManager(app) called a second time never connected the app.
        if app is not None:
            cls._instance.init_app(app)
        return cls._instance

    def init_app(self, app):
        # Connect the Flask app only once, even if called repeatedly
        if self._initialized_app is app:
            return
        self.db.init_app(app)
        with app.app_context():
            self.db.create_all()
        self._initialized_app = app


# Single instance exported for global use
db_manager = DatabaseManager()
db = db_manager.db
