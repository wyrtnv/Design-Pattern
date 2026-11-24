"""Unit tests for the five design patterns (no Flask, no real database where possible)."""

import tempfile
import threading
import unittest
from pathlib import Path

from patterns.delivery_strategy import (
    CourierStrategy,
    DeliveryContext,
    ExpressStrategy,
    PickupStrategy,
)
from patterns.order_observer import (
    ORDER_CANCELLED,
    ORDER_CREATED,
    ORDER_PAID,
    STATUS_CHANGED,
    AuditLogObserver,
    NotificationObserver,
    OrderEventManager,
    OrderObserver,
    StockObserver,
)
from patterns.payment_adapters import (
    BankCardAdapter,
    CryptoWalletAdapter,
    PaymentProcessor,
    PaymentResult,
    PayPalAdapter,
    PayPalSDK,
)
from patterns.payment_factory import PaymentFactory
from patterns.singleton_database import Database


class SingletonTests(unittest.TestCase):
    def setUp(self):
        Database._reset_for_tests()
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        Database._reset_for_tests()
        self.tmp.cleanup()

    def test_same_instance(self):
        a = Database(Path(self.tmp.name) / "a.db")
        b = Database(Path(self.tmp.name) / "other.db")
        self.assertIs(a, b)
        self.assertTrue(b.db_path.endswith("a.db"))   # second path is ignored

    def test_thread_safe_creation(self):
        instances = []
        threads = [threading.Thread(target=lambda: instances.append(Database(Path(self.tmp.name) / "t.db")))
                   for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(len({id(i) for i in instances}), 1)

    def test_transaction_rolls_back_on_error(self):
        db = Database(Path(self.tmp.name) / "r.db")
        db.init_schema()
        db.seed_catalog()
        with self.assertRaises(RuntimeError):
            with db.transaction() as conn:
                conn.execute("DELETE FROM products")
                raise RuntimeError("boom")
        with db.transaction() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM products").fetchone()[0], 10)


class FactoryMethodTests(unittest.TestCase):
    def test_creates_right_processor(self):
        self.assertIsInstance(PaymentFactory.create("card"), BankCardAdapter)
        self.assertIsInstance(PaymentFactory.create(" PayPal "), PayPalAdapter)
        self.assertIsInstance(PaymentFactory.create("crypto"), CryptoWalletAdapter)

    def test_unknown_method(self):
        with self.assertRaisesRegex(ValueError, "Unsupported payment method"):
            PaymentFactory.create("cash")

    def test_register_new_processor_without_changing_factory(self):
        class GiftCardAdapter(PaymentProcessor):
            code, title = "gift", "Gift card"

            def pay(self, payer, amount):
                return PaymentResult(self.code, amount, 0, "GIFT-1", "ok")

        PaymentFactory.register(GiftCardAdapter)
        try:
            self.assertIsInstance(PaymentFactory.create("gift"), GiftCardAdapter)
            self.assertIn("gift", [c for c, _, _ in PaymentFactory.available()])
        finally:
            PaymentFactory._registry.pop("gift")


class AdapterTests(unittest.TestCase):
    def test_card_adapter_converts_to_tiyn(self):
        class SpyGateway:
            def charge_tiyn(self, token, amount_tiyn):
                self.received = amount_tiyn
                return 123456

        spy = SpyGateway()
        result = BankCardAdapter(spy).pay("alice", 1500.5)
        self.assertEqual(spy.received, 150050)
        self.assertEqual(result.transaction_id, "CARD-123456")
        self.assertEqual(result.fee, 22.51)

    def test_paypal_adapter_converts_to_usd_dict(self):
        class SpySDK(PayPalSDK):
            def create_payment(self, payload):
                self.payload = payload
                return super().create_payment(payload)

        sdk = SpySDK()
        result = PayPalAdapter(sdk).pay("bob", 50000)
        self.assertEqual(sdk.payload["total"], "100.00")
        self.assertTrue(result.transaction_id.startswith("PAYID-"))

    def test_paypal_declined(self):
        class DecliningSDK:
            def create_payment(self, payload):
                return {"state": "failed", "id": None}

        with self.assertRaisesRegex(ValueError, "declined"):
            PayPalAdapter(DecliningSDK()).pay("bob", 100)

    def test_crypto_adapter_returns_tx_hash(self):
        result = CryptoWalletAdapter().pay("carol", 25000)
        self.assertTrue(result.transaction_id.startswith("0x"))
        self.assertIn("50.00 USDT", result.message)

    def test_all_adapters_share_one_interface(self):
        for code in ("card", "paypal", "crypto"):
            result = PaymentFactory.create(code).pay("dave", 10000)
            self.assertIsInstance(result, PaymentResult)
            self.assertEqual(result.amount, 10000)


class StrategyTests(unittest.TestCase):
    def test_pickup_is_free(self):
        self.assertEqual(PickupStrategy().calculate(500000, 5), 0)

    def test_courier_free_from_threshold(self):
        self.assertEqual(CourierStrategy().calculate(149999, 1), 1500)
        self.assertEqual(CourierStrategy().calculate(150000, 1), 0)

    def test_express_per_item(self):
        self.assertEqual(ExpressStrategy().calculate(10, 1), 3000)
        self.assertEqual(ExpressStrategy().calculate(10, 3), 4000)

    def test_context_switches_strategy(self):
        ctx = DeliveryContext.for_code("courier")
        self.assertEqual(ctx.cost(1000, 1), 1500)
        ctx.strategy = PickupStrategy()
        self.assertEqual(ctx.cost(1000, 1), 0)

    def test_unknown_strategy(self):
        with self.assertRaises(ValueError):
            DeliveryContext.for_code("teleport")


class ObserverTests(unittest.TestCase):
    ORDER = {"id": 7, "user_id": 2, "status": "PAID", "total": 1000.0,
             "items": [{"product_id": 1, "quantity": 2}]}

    def test_all_subscribers_notified(self):
        calls = []

        class Spy(OrderObserver):
            def __init__(self, name):
                self.name = name

            def update(self, event, order):
                calls.append((self.name, event))

        manager = OrderEventManager()
        manager.subscribe(Spy("a"))
        manager.subscribe(Spy("b"))
        manager.notify(ORDER_CREATED, self.ORDER)
        self.assertEqual(calls, [("a", ORDER_CREATED), ("b", ORDER_CREATED)])

    def test_unsubscribe_and_no_duplicates(self):
        class Counter(OrderObserver):
            n = 0

            def update(self, event, order):
                self.n += 1

        manager, obs = OrderEventManager(), Counter()
        manager.subscribe(obs)
        manager.subscribe(obs)
        manager.notify(ORDER_PAID, self.ORDER)
        manager.unsubscribe(obs)
        manager.notify(ORDER_PAID, self.ORDER)
        self.assertEqual(obs.n, 1)

    def test_notification_observer_messages(self):
        class FakeRepo:
            def __init__(self):
                self.rows = []

            def add(self, user_id, order_id, message):
                self.rows.append((user_id, order_id, message))

        repo = FakeRepo()
        obs = NotificationObserver(repo)
        obs.update(ORDER_PAID, self.ORDER)
        obs.update(STATUS_CHANGED, dict(self.ORDER, status="SHIPPED"))
        obs.update(STATUS_CHANGED, dict(self.ORDER, status="PAID"))   # no message for this one
        self.assertEqual(len(repo.rows), 2)
        self.assertIn("shipped", repo.rows[1][2])

    def test_stock_observer(self):
        class FakeProducts:
            def __init__(self):
                self.changes = []

            def change_stock(self, pid, delta):
                self.changes.append((pid, delta))

        products = FakeProducts()
        obs = StockObserver(products)
        obs.update(ORDER_PAID, self.ORDER)
        obs.update(ORDER_CANCELLED, dict(self.ORDER, was_paid=True))
        obs.update(ORDER_CANCELLED, dict(self.ORDER, was_paid=False))
        self.assertEqual(products.changes, [(1, -2), (1, 2)])

    def test_audit_log_observer_writes_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            import logging
            logger = logging.getLogger("gamehub.orders")
            old_handlers = logger.handlers[:]
            logger.handlers.clear()
            try:
                log_file = Path(tmp) / "orders.log"
                AuditLogObserver(log_file).update(ORDER_PAID, self.ORDER)
                for h in logger.handlers:
                    h.flush()
                self.assertIn("ORDER_PAID | order=7", log_file.read_text(encoding="utf-8"))
            finally:
                for h in logger.handlers:
                    h.close()
                logger.handlers[:] = old_handlers


if __name__ == "__main__":
    unittest.main()
