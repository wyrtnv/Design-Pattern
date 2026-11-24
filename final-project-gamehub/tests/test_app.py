"""Integration tests: repositories, services and Flask routes on a temporary database."""

import tempfile
import unittest
from pathlib import Path

from app import create_app
from models.entities import OrderItem
from patterns.order_observer import OrderEventManager
from patterns.singleton_database import Database
from repositories.repositories import (
    CategoryRepository,
    NotificationRepository,
    ProductRepository,
    UserRepository,
)
from services.auth_service import AuthService
from services.cart_service import CartService
from services.catalog_service import CatalogService
from services.order_service import OrderService


class AppTestCase(unittest.TestCase):
    def setUp(self):
        Database._reset_for_tests()
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app(Path(self.tmp.name) / "test.db", testing=True)
        self.client = self.app.test_client()
        self.service = self.app.extensions["gamehub"]["order_service"]

    def tearDown(self):
        Database._reset_for_tests()
        self.tmp.cleanup()

    def login(self, username="student", password="student123"):
        return self.client.post("/login", data={"username": username, "password": password})


class RepositoryTests(AppTestCase):
    def test_save_and_reload_product(self):
        repo = ProductRepository()
        pid = repo.create(1, "Test Laptop", "desc", 123456, 4, "💻")
        loaded = repo.get(pid)
        self.assertEqual((loaded.name, loaded.price, loaded.stock, loaded.category_name),
                         ("Test Laptop", 123456, 4, "Laptops"))

    def test_search_and_sort(self):
        repo = ProductRepository()
        self.assertEqual(len(repo.search(category_id=3)), 2)
        prices = [p.price for p in repo.search(sort="price_asc")]
        self.assertEqual(prices, sorted(prices))
        self.assertTrue(all("Razer" in p.name for p in repo.search("Razer")))

    def test_sql_injection_is_harmless(self):
        repo = ProductRepository()
        self.assertEqual(repo.search("' OR 1=1 --"), [])
        self.assertEqual(len(repo.search(sort="price; DROP TABLE products")), 10)

    def test_category_counts(self):
        cats = CategoryRepository().get_all()
        self.assertEqual(sum(c.product_count for c in cats), 10)


class ServiceTests(AppTestCase):
    def test_register_validation_and_hashing(self):
        auth = AuthService()
        uid = auth.register("newbie", "secret1", "New User")
        user = UserRepository().get(uid)
        self.assertNotEqual(user.password_hash, "secret1")
        self.assertEqual(auth.login("newbie", "secret1").id, uid)
        for bad in [("ab", "secret1", "X"), ("good_name", "123", "X"), ("newbie", "secret1", "Dup")]:
            with self.assertRaises(ValueError):
                auth.register(*bad)
        with self.assertRaises(ValueError):
            auth.login("newbie", "wrong")

    def test_product_validation(self):
        catalog = CatalogService()
        form = {"name": "Mouse", "category_id": "3", "price": "-5", "stock": "1"}
        with self.assertRaisesRegex(ValueError, "Price"):
            catalog.create_product(form)
        with self.assertRaisesRegex(ValueError, "numbers"):
            catalog.create_product(dict(form, price="abc"))
        with self.assertRaisesRegex(ValueError, "category"):
            catalog.create_product(dict(form, price="5", category_id="99"))

    def test_category_rules(self):
        catalog = CatalogService()
        with self.assertRaisesRegex(ValueError, "already exists"):
            catalog.create_category("Mice")
        with self.assertRaisesRegex(ValueError, "still has products"):
            catalog.delete_category(3)
        cid = catalog.create_category("Chairs")
        catalog.update_category(cid, "Gaming chairs")
        catalog.delete_category(cid)

    def test_cart_never_exceeds_stock(self):
        cart = CartService({})
        cart.add(1, 2)
        with self.assertRaisesRegex(ValueError, "left in stock"):
            cart.add(1, 10)
        self.assertEqual(cart.count(), 2)

    def test_full_checkout_flow(self):
        user = UserRepository().get_by_username("student")
        items = [OrderItem(3, 2, 69990), OrderItem(6, 1, 34990)]
        order = self.service.checkout(user, items, "courier", "paypal", "Almaty, Abay 10")
        self.assertEqual(order.status, "PAID")
        self.assertEqual(order.subtotal, 174970)
        self.assertEqual(order.delivery_cost, 0)          # courier is free from 150 000 ₸
        self.assertEqual(order.payment.method, "paypal")
        self.assertEqual(ProductRepository().get(3).stock, 10)   # StockObserver: 12 - 2
        messages = NotificationRepository().for_user(user.id)
        self.assertEqual(len(messages), 2)               # created + paid

        self.service.change_status(order.id, "SHIPPED")
        self.service.change_status(order.id, "DELIVERED")
        with self.assertRaises(ValueError):
            self.service.change_status(order.id, "CANCELLED")
        self.assertEqual(len(NotificationRepository().for_user(user.id)), 4)

    def test_cancel_returns_stock(self):
        user = UserRepository().get_by_username("student")
        order = self.service.checkout(user, [OrderItem(9, 1, 149990)], "pickup", "card")
        self.assertEqual(ProductRepository().get(9).stock, 3)
        self.service.cancel(order)
        self.assertEqual(ProductRepository().get(9).stock, 4)
        with self.assertRaises(ValueError):
            self.service.cancel(order)

    def test_checkout_validation(self):
        user = UserRepository().get_by_username("student")
        with self.assertRaisesRegex(ValueError, "empty"):
            self.service.checkout(user, [], "pickup", "card")
        with self.assertRaisesRegex(ValueError, "address"):
            self.service.checkout(user, [OrderItem(1, 1, 1)], "courier", "card", "")
        with self.assertRaisesRegex(ValueError, "left in stock"):
            self.service.checkout(user, [OrderItem(1, 99, 1)], "pickup", "card")
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            self.service.checkout(user, [OrderItem(1, 1, 1)], "pickup", "cash")

    def test_service_uses_injected_event_manager(self):
        events = OrderEventManager()
        self.assertEqual(OrderService(events).events.observers, [])


class RouteTests(AppTestCase):
    def test_public_pages(self):
        for url in ("/", "/?q=razer&sort=price_desc", "/product/1", "/cart", "/login", "/register"):
            self.assertEqual(self.client.get(url).status_code, 200, url)
        self.assertEqual(self.client.get("/product/999").status_code, 404)

    def test_customer_cannot_open_admin(self):
        self.login()
        self.assertEqual(self.client.get("/admin/").status_code, 403)
        self.assertEqual(self.client.post("/admin/products/1/delete").status_code, 403)

    def test_login_required(self):
        response = self.client.get("/orders/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_bad_login(self):
        self.assertEqual(self.login("student", "nope").status_code, 401)

    def test_shopping_flow_through_http(self):
        self.login()
        self.client.post("/cart/add/5", data={"quantity": "1"})
        self.assertIn("Superlight".encode(), self.client.get("/cart").data)
        self.assertEqual(self.client.get("/checkout").status_code, 200)
        response = self.client.post("/checkout", data={"delivery": "express", "payment": "crypto",
                                                       "address": "Almaty, Satpaev 22"})
        self.assertEqual(response.status_code, 302)
        page = self.client.get(response.headers["Location"]).data.decode()
        self.assertIn("PAID", page)
        self.assertIn("0x", page)
        self.assertIn("Payment for order", self.client.get("/orders/notifications").data.decode())

    def test_admin_crud(self):
        self.login("admin", "admin123")
        self.assertEqual(self.client.get("/admin/").status_code, 200)
        data = {"name": "Corsair K70", "category_id": "2", "price": "59990", "stock": "7", "icon": "⌨️"}
        self.client.post("/admin/products/add", data=data)
        product = ProductRepository().search("Corsair")[0]
        self.client.post(f"/admin/products/{product.id}/edit", data=dict(data, price="55990"))
        self.assertEqual(ProductRepository().get(product.id).price, 55990)
        self.client.post(f"/admin/products/{product.id}/delete")
        self.assertIsNone(ProductRepository().get(product.id))
        self.client.post("/admin/categories", data={"name": "Chairs"})
        self.assertIn(b"Chairs", self.client.get("/admin/categories").data)

    def test_csrf_enforced_outside_tests(self):
        self.app.config["TESTING"] = False
        self.assertEqual(self.client.post("/login", data={"username": "x", "password": "y"}).status_code, 400)


if __name__ == "__main__":
    unittest.main()
