"""
Pattern 1 — Factory Method (Creational).

The checkout form sends only a string: "card", "paypal" or "crypto".
PaymentFactory decides which PaymentProcessor (adapter) to create, so the
service layer never writes BankCardAdapter() / PayPalAdapter() itself.

Adding a new provider = one new adapter class + one register() call.
OrderService, controllers and templates stay untouched (Open/Closed principle).
"""

from patterns.payment_adapters import (
    BankCardAdapter,
    CryptoWalletAdapter,
    PaymentProcessor,
    PayPalAdapter,
)


class PaymentFactory:
    _registry = {
        BankCardAdapter.code: BankCardAdapter,
        PayPalAdapter.code: PayPalAdapter,
        CryptoWalletAdapter.code: CryptoWalletAdapter,
    }

    @classmethod
    def create(cls, method: str) -> PaymentProcessor:
        processor_class = cls._registry.get(str(method).strip().lower())
        if processor_class is None:
            supported = ", ".join(cls._registry)
            raise ValueError(f"Unsupported payment method '{method}'. Use one of: {supported}")
        return processor_class()

    @classmethod
    def register(cls, processor_class):
        cls._registry[processor_class.code] = processor_class

    @classmethod
    def available(cls):
        """[(code, title, fee_percent)] for the checkout page."""
        return [(c.code, c.title, c.fee_percent) for c in cls._registry.values()]
