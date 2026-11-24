"""
Pattern 3 — Adapter (Structural).

GameHub accepts payments through three external providers. Each provider ships
its own SDK with its own, incompatible interface:

    BankCardGateway.charge_tiyn(card_token, amount_tiyn)      -> int (approval code)
    PayPalSDK.create_payment({"total": "12.34", ...})          -> dict
    CryptoWalletAPI.send_usdt(wallet, amount_str, memo)        -> str (tx hash)

The rest of the application wants only one interface — PaymentProcessor.pay().
Each Adapter wraps one SDK and translates the call: tenge -> tiyn, tenge -> USD,
tenge -> USDT string, and the SDK's answer -> PaymentResult.

The SDK classes below are local simulations (no real money is moved), but their
interfaces are deliberately different, as they would be with real providers.
"""

import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass

KZT_PER_USD = 500.0  # fixed demo exchange rate


@dataclass
class PaymentResult:
    method: str
    amount: float          # in tenge
    fee: float             # in tenge
    transaction_id: str
    message: str


# --------------------------------------------------------------------------
# Target interface — what GameHub expects
# --------------------------------------------------------------------------
class PaymentProcessor(ABC):
    code = ""
    title = ""
    fee_percent = 0.0

    def fee_for(self, amount: float) -> float:
        return round(amount * self.fee_percent / 100, 2)

    @abstractmethod
    def pay(self, payer: str, amount: float) -> PaymentResult:
        """Charge `amount` tenge from `payer`."""


# --------------------------------------------------------------------------
# Adaptees — third-party SDKs with incompatible interfaces (simulated)
# --------------------------------------------------------------------------
class BankCardGateway:
    """Local bank acquiring: works in tiyn (1 ₸ = 100 tiyn), returns an int code."""

    def charge_tiyn(self, card_token: str, amount_tiyn: int) -> int:
        if amount_tiyn <= 0:
            raise ValueError("Bank gateway: amount must be positive")
        return secrets.randbelow(900000) + 100000


class PayPalSDK:
    """PayPal-style SDK: takes a dict with a USD string, returns a dict."""

    def create_payment(self, payload: dict) -> dict:
        if float(payload["total"]) <= 0:
            return {"state": "failed", "id": None}
        return {"state": "approved", "id": "PAYID-" + secrets.token_hex(6).upper()}


class CryptoWalletAPI:
    """Crypto wallet API: sends USDT, amount as a string, returns a tx hash."""

    def send_usdt(self, wallet: str, amount: str, memo: str) -> str:
        if float(amount) <= 0:
            raise ValueError("Crypto API: amount must be positive")
        return "0x" + secrets.token_hex(16)


# --------------------------------------------------------------------------
# Adapters
# --------------------------------------------------------------------------
class BankCardAdapter(PaymentProcessor):
    code = "card"
    title = "Bank card"
    fee_percent = 1.5

    def __init__(self, gateway: BankCardGateway = None):
        self._gateway = gateway or BankCardGateway()

    def pay(self, payer, amount):
        tiyn = int(round(amount * 100))                       # ₸ -> tiyn
        code = self._gateway.charge_tiyn(f"tok_{payer}", tiyn)
        return PaymentResult(self.code, amount, self.fee_for(amount),
                             f"CARD-{code}", f"Paid {amount:,.0f} ₸ by bank card")


class PayPalAdapter(PaymentProcessor):
    code = "paypal"
    title = "PayPal"
    fee_percent = 3.4

    def __init__(self, sdk: PayPalSDK = None):
        self._sdk = sdk or PayPalSDK()

    def pay(self, payer, amount):
        usd = f"{amount / KZT_PER_USD:.2f}"                    # ₸ -> USD string
        response = self._sdk.create_payment({"total": usd, "currency": "USD", "payer": payer})
        if response["state"] != "approved":
            raise ValueError("PayPal declined the payment")
        return PaymentResult(self.code, amount, self.fee_for(amount),
                             response["id"], f"Paid ${usd} via PayPal")


class CryptoWalletAdapter(PaymentProcessor):
    code = "crypto"
    title = "Crypto wallet (USDT)"
    fee_percent = 1.0

    def __init__(self, api: CryptoWalletAPI = None):
        self._api = api or CryptoWalletAPI()

    def pay(self, payer, amount):
        usdt = f"{amount / KZT_PER_USD:.2f}"                   # ₸ -> USDT string
        tx_hash = self._api.send_usdt(f"wallet:{payer}", usdt, memo="GameHub order")
        return PaymentResult(self.code, amount, self.fee_for(amount),
                             tx_hash, f"Sent {usdt} USDT from crypto wallet")
