"""
Pattern 5 — Strategy (Behavioral).

Delivery cost is calculated by a different algorithm for each delivery method.
Instead of an if/elif chain inside OrderService, each algorithm is a separate
class with the same interface, and the customer picks one at checkout.

    Pickup   — free, ready in 1 day
    Courier  — 1 500 ₸ inside Almaty, free from 150 000 ₸
    Express  — 3 000 ₸ + 500 ₸ for every item after the first, same day
"""

from abc import ABC, abstractmethod


class DeliveryStrategy(ABC):
    code = ""
    title = ""
    eta = ""
    needs_address = True

    @abstractmethod
    def calculate(self, subtotal: float, items_count: int) -> float:
        """Return delivery cost in tenge."""


class PickupStrategy(DeliveryStrategy):
    code = "pickup"
    title = "Pickup from store"
    eta = "tomorrow"
    needs_address = False

    def calculate(self, subtotal, items_count):
        return 0.0


class CourierStrategy(DeliveryStrategy):
    code = "courier"
    title = "Courier (Almaty)"
    eta = "1–2 days"
    BASE = 1500.0
    FREE_FROM = 150000.0

    def calculate(self, subtotal, items_count):
        return 0.0 if subtotal >= self.FREE_FROM else self.BASE


class ExpressStrategy(DeliveryStrategy):
    code = "express"
    title = "Express (same day)"
    eta = "today"
    BASE = 3000.0
    PER_EXTRA_ITEM = 500.0

    def calculate(self, subtotal, items_count):
        return self.BASE + self.PER_EXTRA_ITEM * max(items_count - 1, 0)


class DeliveryContext:
    """Context: holds the chosen strategy and delegates the calculation to it."""

    _strategies = {s.code: s for s in (PickupStrategy, CourierStrategy, ExpressStrategy)}

    def __init__(self, strategy: DeliveryStrategy):
        self.strategy = strategy

    @classmethod
    def for_code(cls, code: str) -> "DeliveryContext":
        strategy_class = cls._strategies.get(str(code).strip().lower())
        if strategy_class is None:
            raise ValueError(f"Unknown delivery method '{code}'")
        return cls(strategy_class())

    @classmethod
    def all_strategies(cls):
        return [s() for s in cls._strategies.values()]

    def cost(self, subtotal: float, items_count: int) -> float:
        return round(self.strategy.calculate(subtotal, items_count), 2)
