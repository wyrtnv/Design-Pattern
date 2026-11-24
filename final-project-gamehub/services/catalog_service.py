"""Catalog business logic: validation of products and categories before they reach the repository."""

import sqlite3

from repositories.repositories import CategoryRepository, ProductRepository


class CatalogService:
    def __init__(self, products: ProductRepository = None, categories: CategoryRepository = None):
        self.products = products or ProductRepository()
        self.categories = categories or CategoryRepository()

    # --- read --------------------------------------------------------------
    def search(self, text="", category_id=None, sort="new"):
        return self.products.search(text.strip(), category_id, sort)

    def get_product(self, product_id):
        product = self.products.get(product_id)
        if product is None:
            raise LookupError("Product not found.")
        return product

    def get_categories(self):
        return self.categories.get_all()

    # --- products ----------------------------------------------------------
    def _validate_product(self, form):
        name = form.get("name", "").strip()
        description = form.get("description", "").strip()
        icon = form.get("icon", "").strip() or "🎮"
        try:
            category_id = int(form.get("category_id", ""))
            price = float(form.get("price", ""))
            stock = int(form.get("stock", ""))
        except ValueError:
            raise ValueError("Category, price and stock must be numbers.")
        if not name or len(name) > 100:
            raise ValueError("Product name is required (max 100 characters).")
        if price < 0 or price > 10_000_000:
            raise ValueError("Price must be between 0 and 10 000 000 ₸.")
        if stock < 0 or stock > 10_000:
            raise ValueError("Stock must be between 0 and 10 000.")
        if self.categories.get(category_id) is None:
            raise ValueError("Selected category does not exist.")
        return category_id, name, description, round(price, 2), stock, icon[:4]

    def create_product(self, form):
        return self.products.create(*self._validate_product(form))

    def update_product(self, product_id, form):
        self.get_product(product_id)
        self.products.update(product_id, *self._validate_product(form))

    def delete_product(self, product_id):
        self.get_product(product_id)
        try:
            self.products.delete(product_id)
        except sqlite3.IntegrityError:
            raise ValueError("This product is used in orders and cannot be deleted. Set stock to 0 instead.")

    # --- categories --------------------------------------------------------
    @staticmethod
    def _clean_name(name):
        name = (name or "").strip()
        if not name or len(name) > 50:
            raise ValueError("Category name is required (max 50 characters).")
        return name

    def create_category(self, name):
        try:
            return self.categories.create(self._clean_name(name))
        except sqlite3.IntegrityError:
            raise ValueError("A category with this name already exists.")

    def update_category(self, category_id, name):
        if self.categories.get(category_id) is None:
            raise LookupError("Category not found.")
        try:
            self.categories.update(category_id, self._clean_name(name))
        except sqlite3.IntegrityError:
            raise ValueError("A category with this name already exists.")

    def delete_category(self, category_id):
        try:
            self.categories.delete(category_id)
        except sqlite3.IntegrityError:
            raise ValueError("The category still has products. Move or delete them first.")
