"""
Creates the schema and demo data. Called automatically by app.py on start;
can also be run by hand:  .venv/bin/python seed.py

Demo accounts (for local demonstration only):
    admin   / admin123    — administrator
    student / student123  — customer
"""

from patterns.singleton_database import Database
from repositories.repositories import UserRepository
from services.auth_service import AuthService

DEMO_USERS = [
    ("admin", "admin123", "GameHub Admin", "admin"),
    ("student", "student123", "Demo Student", "customer"),
]


def seed(db: Database = None):
    db = db or Database()
    db.init_schema()
    db.seed_catalog()
    users = UserRepository(db)
    if users.count() == 0:
        auth = AuthService(users)
        for username, password, full_name, role in DEMO_USERS:
            auth.register(username, password, full_name, role)


if __name__ == "__main__":
    seed()
    print("Database ready:", Database().db_path)
