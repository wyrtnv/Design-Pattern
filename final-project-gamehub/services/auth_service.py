"""Authentication: registration and login. Passwords are stored only as salted hashes."""

import re

from werkzeug.security import check_password_hash, generate_password_hash

from repositories.repositories import UserRepository

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,30}$")


class AuthService:
    def __init__(self, users: UserRepository = None):
        self.users = users or UserRepository()

    def register(self, username, password, full_name, role="customer"):
        username, full_name = username.strip(), full_name.strip()
        if not USERNAME_RE.match(username):
            raise ValueError("Username: 3–30 characters, letters, digits or _ only.")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        if not full_name:
            raise ValueError("Full name is required.")
        if self.users.get_by_username(username):
            raise ValueError("This username is already taken.")
        return self.users.create(username, generate_password_hash(password), full_name, role)

    def login(self, username, password):
        user = self.users.get_by_username(username.strip())
        if user is None or not check_password_hash(user.password_hash, password):
            raise ValueError("Invalid username or password.")
        return user
