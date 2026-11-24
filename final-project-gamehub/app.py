"""
GameHub — online gaming-equipment store.
Entry point: creates the Flask app, wires the patterns together and registers controllers.

Run:  .venv/bin/python app.py   ->  http://127.0.0.1:5005
"""

import os
import secrets

from flask import Flask, abort, render_template, request, session

from controllers.admin_controller import admin_bp
from controllers.auth_controller import auth_bp
from controllers.helpers import current_user
from controllers.order_controller import orders_bp
from controllers.shop_controller import shop_bp
from patterns.order_observer import (
    AuditLogObserver,
    NotificationObserver,
    OrderEventManager,
    StockObserver,
)
from patterns.singleton_database import Database
from repositories.repositories import NotificationRepository, ProductRepository
from seed import seed
from services.order_service import OrderService


def create_app(db_path=None, testing=False):
    app = Flask(__name__)
    # SAST fix S-02: the key comes from the environment; without it a random key is
    # generated on every start (sessions then simply expire after a restart).
    app.secret_key = os.environ.get("GAMEHUB_SECRET_KEY") or secrets.token_hex(32)
    app.config["TESTING"] = testing

    # Singleton: the one Database object for the whole app
    db = Database(db_path)
    seed(db)

    # Observer: subscribe all reactions to order events
    events = OrderEventManager()
    events.subscribe(NotificationObserver(NotificationRepository(db)))
    events.subscribe(StockObserver(ProductRepository(db)))
    events.subscribe(AuditLogObserver())
    app.extensions["gamehub"] = {"order_service": OrderService(events), "events": events}

    for blueprint in (auth_bp, shop_bp, orders_bp, admin_bp):
        app.register_blueprint(blueprint)

    # --- CSRF protection for every POST form ---------------------------------
    @app.before_request
    def csrf_protect():
        if request.method == "POST" and not app.config["TESTING"]:
            token = session.get("_csrf")
            if not token or token != request.form.get("_csrf"):
                abort(400, description="Invalid or missing CSRF token. Reload the page and try again.")

    @app.context_processor
    def inject_globals():
        if "_csrf" not in session:
            session["_csrf"] = secrets.token_hex(16)
        user = current_user()
        unread = NotificationRepository().unread_count(user.id) if user else 0
        cart_count = sum(session.get("cart", {}).values())
        return {"user": user, "csrf_token": session["_csrf"], "unread": unread, "cart_count": cart_count}

    @app.template_filter("money")
    def money(value):
        return f"{value:,.0f} ₸".replace(",", " ")

    for code in (400, 403, 404):
        app.register_error_handler(
            code, lambda e, c=code: (render_template("error.html", code=c, error=e), c)
        )

    return app


if __name__ == "__main__":
    # SAST fix S-01: the Werkzeug debugger is OFF unless explicitly enabled
    # for local development:  GAMEHUB_DEBUG=1 .venv/bin/python app.py
    debug = os.environ.get("GAMEHUB_DEBUG") == "1"
    create_app().run(debug=debug, port=5005)
