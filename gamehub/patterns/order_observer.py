"""
Pattern 4 — Observer (Behavioral).

OrderEventManager is the Subject. Whenever an order is created, paid, shipped,
delivered or cancelled, OrderService calls notify(event, order). Every
subscribed observer reacts in its own way:

    NotificationObserver — writes a message to the customer's notification inbox
    StockObserver        — takes items off stock on payment, returns them on cancel
    AuditLogObserver     — writes a line to logs/orders.log for the administrator

OrderService knows nothing about inboxes, stock or log files. A new reaction
(e-mail, Telegram bot, analytics) is a new observer + one subscribe() call.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path

ORDER_CREATED = "ORDER_CREATED"
ORDER_PAID = "ORDER_PAID"
STATUS_CHANGED = "STATUS_CHANGED"
ORDER_CANCELLED = "ORDER_CANCELLED"

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"


class OrderObserver(ABC):
    @abstractmethod
    def update(self, event: str, order: dict) -> None:
        """React to an order event. `order` has id, user_id, status, total, items."""


class OrderEventManager:
    """Subject."""

    def __init__(self):
        self._observers = []

    def subscribe(self, observer: OrderObserver):
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: OrderObserver):
        if observer in self._observers:
            self._observers.remove(observer)

    @property
    def observers(self):
        return list(self._observers)

    def notify(self, event: str, order: dict):
        for observer in self._observers:
            observer.update(event, order)


# --------------------------------------------------------------------------
# Concrete observers
# --------------------------------------------------------------------------
class NotificationObserver(OrderObserver):
    MESSAGES = {
        ORDER_CREATED: "Order #{id} has been created. Total: {total_text}.",
        ORDER_PAID: "Payment for order #{id} received. We are preparing your items.",
        ORDER_CANCELLED: "Order #{id} was cancelled. Items returned to stock.",
    }
    STATUS_TEXT = {
        "SHIPPED": "Order #{id} has been shipped and is on its way.",
        "DELIVERED": "Order #{id} was delivered. Enjoy your new gear! 🎮",
    }

    def __init__(self, notification_repository):
        self._repo = notification_repository

    def update(self, event, order):
        if event == STATUS_CHANGED:
            template = self.STATUS_TEXT.get(order["status"])
        else:
            template = self.MESSAGES.get(event)
        if template:
            total_text = f"{order['total']:,.0f} ₸".replace(",", " ")
            self._repo.add(order["user_id"], order["id"], template.format(total_text=total_text, **order))


class StockObserver(OrderObserver):
    def __init__(self, product_repository):
        self._products = product_repository

    def update(self, event, order):
        if event == ORDER_PAID:
            for item in order["items"]:
                self._products.change_stock(item["product_id"], -item["quantity"])
        elif event == ORDER_CANCELLED and order.get("was_paid"):
            for item in order["items"]:
                self._products.change_stock(item["product_id"], item["quantity"])


class AuditLogObserver(OrderObserver):
    def __init__(self, log_file: Path = None):
        self._logger = logging.getLogger("gamehub.orders")
        if not self._logger.handlers:
            log_file = log_file or LOG_DIR / "orders.log"
            log_file.parent.mkdir(exist_ok=True)
            handler = logging.FileHandler(log_file, encoding="utf-8")
            handler.setFormatter(logging.Formatter("%(asctime)s | %(message)s"))
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.INFO)

    def update(self, event, order):
        self._logger.info("%s | order=%s user=%s status=%s total=%.2f",
                          event, order["id"], order["user_id"], order["status"], order["total"])
