"""Shared controller helpers: current user, access decorators, access to services."""

from functools import wraps

from flask import abort, current_app, flash, redirect, request, session, url_for

from repositories.repositories import UserRepository
from services.cart_service import CartService


def current_user():
    user_id = session.get("user_id")
    return UserRepository().get(user_id) if user_id else None


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if current_user() is None:
            flash("Please log in first.", "error")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return wrapper


def admin_required(view):
    """Server-side access check: hiding buttons in HTML is not enough."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        user = current_user()
        if user is None:
            return redirect(url_for("auth.login", next=request.path))
        if not user.is_admin:
            abort(403, description="Only administrators can open this page.")
        return view(*args, **kwargs)
    return wrapper


def order_service():
    return current_app.extensions["gamehub"]["order_service"]


def cart():
    session.setdefault("cart", {})
    session.modified = True
    return CartService(session["cart"])


def parse_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
