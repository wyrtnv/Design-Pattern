"""
OrderService — the heart of the shop. checkout() is a single entry point that
coordinates four patterns:

    1. Strategy        DeliveryContext.for_code(...).cost(...)    — delivery price
    2. Factory Method  PaymentFactory.create(method)              — which processor
    3. Adapter         processor.pay(...)                          — talks to the SDK
    4. Observer        events.notify(ORDER_CREATED / ORDER_PAID)  — inbox, stock, log

and the Repository layer for saving everything.
"""

from patterns.delivery_strategy import DeliveryContext
from patterns.order_observer import (
    ORDER_CANCELLED,
    ORDER_CREATED,
    ORDER_PAID,
    STATUS_CHANGED,
    OrderEventManager,
)
from patterns.payment_factory import PaymentFactory
from repositories.repositories import OrderRepository, PaymentRepository, ProductRepository

# Allowed manual status changes made by the administrator
TRANSITIONS = {
    "NEW": {"CANCELLED"},
    "PAID": {"SHIPPED", "CANCELLED"},
    "SHIPPED": {"DELIVERED"},
    "DELIVERED": set(),
    "CANCELLED": set(),
}


class OrderService:
    def __init__(self, events: OrderEventManager, orders: OrderRepository = None,
                 payments: PaymentRepository = None, products: ProductRepository = None):
        self.events = events
        self.orders = orders or OrderRepository()
        self.payments = payments or PaymentRepository()
        self.products = products or ProductRepository()

    # ---------------------------------------------------------------------
    def quote(self, items, delivery_code):
        """Prices for the checkout page (no saving)."""
        subtotal = round(sum(i.line_total for i in items), 2)
        count = sum(i.quantity for i in items)
        delivery = DeliveryContext.for_code(delivery_code).cost(subtotal, count)
        return {"subtotal": subtotal, "delivery": delivery, "total": round(subtotal + delivery, 2)}

    def checkout(self, user, items, delivery_code, payment_method, address=""):
        # --- validation ---------------------------------------------------
        if not items:
            raise ValueError("Your cart is empty.")
        for item in items:
            product = self.products.get(item.product_id)
            if product is None:
                raise ValueError("A product in your cart no longer exists.")
            if item.quantity > product.stock:
                raise ValueError(f"Only {product.stock} × {product.name} left in stock.")
        context = DeliveryContext.for_code(delivery_code)               # Strategy
        address = (address or "").strip()
        if context.strategy.needs_address and len(address) < 5:
            raise ValueError("Please enter a delivery address.")
        processor = PaymentFactory.create(payment_method)               # Factory Method

        # --- create the order ---------------------------------------------
        prices = self.quote(items, delivery_code)
        order_id = self.orders.create(user.id, context.strategy.code, prices["delivery"],
                                      prices["subtotal"], prices["total"], address, items)
        order = self.orders.get(order_id)
        self.events.notify(ORDER_CREATED, order.as_event())             # Observer

        # --- pay ----------------------------------------------------------
        result = processor.pay(user.username, prices["total"])          # Adapter
        self.payments.create(order_id, result.method, result.amount, result.fee, result.transaction_id)
        self.orders.set_status(order_id, "PAID")
        order = self.orders.get(order_id)
        self.events.notify(ORDER_PAID, order.as_event())                # Observer
        return order

    # ---------------------------------------------------------------------
    def get_for_user(self, user):
        return self.orders.get_for_user(user.id)

    def get(self, order_id, user):
        order = self.orders.get(order_id)
        if order is None or (not user.is_admin and order.user_id != user.id):
            raise LookupError("Order not found.")
        return order

    def get_all(self, status=None):
        return self.orders.get_all(status or None)

    def change_status(self, order_id, new_status):
        order = self.orders.get(order_id)
        if order is None:
            raise LookupError("Order not found.")
        if new_status not in TRANSITIONS.get(order.status, set()):
            raise ValueError(f"Cannot change status from {order.status} to {new_status}.")
        if new_status == "CANCELLED":
            return self.cancel(order)
        self.orders.set_status(order_id, new_status)
        order.status = new_status
        self.events.notify(STATUS_CHANGED, order.as_event())
        return order

    def cancel(self, order):
        if not order.can_cancel:
            raise ValueError("Only new or paid orders can be cancelled.")
        was_paid = order.status == "PAID"
        self.orders.set_status(order.id, "CANCELLED")
        order.status = "CANCELLED"
        self.events.notify(ORDER_CANCELLED, order.as_event(was_paid=was_paid))
        return order

    def delete(self, order_id):
        order = self.orders.get(order_id)
        if order is None:
            raise LookupError("Order not found.")
        if order.status not in ("CANCELLED", "DELIVERED"):
            raise ValueError("Only cancelled or delivered orders can be deleted.")
        self.orders.delete(order_id)

    def stats(self):
        return self.orders.stats()
