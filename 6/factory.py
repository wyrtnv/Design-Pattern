"""
Factory Method Pattern — payment services.

The client only says which method it wants ("paypal", "stripe", "crypto").
PaymentFactory decides which concrete class to create, so app.py never
writes PayPalPayment() / StripePayment() / CryptoWalletPayment() itself.
"""

from abc import ABC, abstractmethod


# 1. Product interface (abstract base class)
class BasePaymentService(ABC):
    name = ""
    fee_percent = 0.0

    def calculate_fee(self, amount: float) -> float:
        return round(amount * self.fee_percent / 100, 2)

    @abstractmethod
    def pay(self, payer: str, amount: float) -> str:
        pass


# 2. Concrete products — each method has its own fee and message
class PayPalPayment(BasePaymentService):
    name = "paypal"
    fee_percent = 3.4

    def pay(self, payer, amount):
        return f"[PAYPAL] {payer} paid ${amount:.2f} via PayPal account"


class StripePayment(BasePaymentService):
    name = "stripe"
    fee_percent = 2.9

    def pay(self, payer, amount):
        return f"[STRIPE] {payer} paid ${amount:.2f} by card through Stripe"


class CryptoWalletPayment(BasePaymentService):
    name = "crypto"
    fee_percent = 1.0

    def pay(self, payer, amount):
        return f"[CRYPTO] {payer} sent ${amount:.2f} in USDT from a crypto wallet"


# 3. Creator / Factory
class PaymentFactory:
    _services = {
        "paypal": PayPalPayment,
        "stripe": StripePayment,
        "crypto": CryptoWalletPayment,
    }

    @staticmethod
    def create_payment_service(method: str) -> BasePaymentService:
        service_class = PaymentFactory._services.get(str(method).strip().lower())
        if service_class is None:
            supported = ", ".join(PaymentFactory._services)
            raise ValueError(f"Unsupported payment method: '{method}'. Use one of: {supported}")
        return service_class()
