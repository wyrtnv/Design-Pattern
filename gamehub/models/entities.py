"""
Model layer — plain domain objects. Repositories turn SQLite rows into these
objects, so services and templates never work with raw rows or SQL.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class User:
    id: int
    username: str
    full_name: str
    role: str
    password_hash: str = field(default="", repr=False)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


@dataclass
class Category:
    id: int
    name: str
    product_count: int = 0


@dataclass
class Product:
    id: int
    category_id: int
    name: str
    description: str
    price: float
    stock: int
    icon: str = "🎮"
    category_name: str = ""

    @property
    def in_stock(self) -> bool:
        return self.stock > 0


@dataclass
class OrderItem:
    product_id: int
    quantity: int
    unit_price: float
    product_name: str = ""
    icon: str = ""

    @property
    def line_total(self) -> float:
        return round(self.unit_price * self.quantity, 2)


@dataclass
class Payment:
    id: int
    order_id: int
    method: str
    amount: float
    fee: float
    transaction_id: str
    status: str
    created_at: str


@dataclass
class Order:
    id: int
    user_id: int
    status: str
    delivery_method: str
    delivery_cost: float
    subtotal: float
    total: float
    address: str
    created_at: str
    customer_name: str = ""
    items: List[OrderItem] = field(default_factory=list)
    payment: Optional[Payment] = None

    @property
    def can_cancel(self) -> bool:
        return self.status in ("NEW", "PAID")

    def as_event(self, **extra) -> dict:
        """Snapshot sent to observers."""
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "status": self.status,
            "total": self.total,
            "items": [{"product_id": i.product_id, "quantity": i.quantity} for i in self.items],
        }
        data.update(extra)
        return data


@dataclass
class Notification:
    id: int
    user_id: int
    order_id: Optional[int]
    message: str
    is_read: bool
    created_at: str
