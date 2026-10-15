"""
Decorator Pattern — price calculation for the online shop.

Problem: a product can get a discount, a tax and a shipping fee in any
combination. Making a subclass for every combination
(DiscountedTaxedProduct, TaxedShippedProduct, ...) would explode the
number of classes. Instead every extra is a small "wrapper" (decorator)
around a product. Wrappers can be stacked in any order and number,
and the Product class itself is never modified.

    ShippingDecorator( TaxDecorator( DiscountDecorator( Product ) ) )
"""

from abc import ABC, abstractmethod

TAX_RATE = 12          # VAT in Kazakhstan, %
SHIPPING_COST = 1500   # fixed delivery fee, ₸


class PriceComponent(ABC):
    """Common interface for the product and all decorators."""

    @abstractmethod
    def get_price(self) -> float:
        ...

    @abstractmethod
    def get_steps(self) -> list:
        """List of (description, price after this step) for the UI."""
        ...


class Product(PriceComponent):
    """The original object. It knows nothing about decorators."""

    def __init__(self, id, name, price, category):
        self.id = id
        self.name = name
        self.price = price
        self.category = category

    def get_price(self):
        return self.price

    def get_steps(self):
        return [("Base price", self.price)]


class ProductDecorator(PriceComponent):
    """Base decorator: wraps another component and delegates to it."""

    def __init__(self, component: PriceComponent):
        self._component = component

    def get_price(self):
        return self._component.get_price()

    def get_steps(self):
        return self._component.get_steps()


class DiscountDecorator(ProductDecorator):
    def __init__(self, component, percent):
        super().__init__(component)
        self.percent = percent

    def get_price(self):
        price = super().get_price()
        return price - price * self.percent / 100

    def get_steps(self):
        return super().get_steps() + [(f"Discount −{self.percent}%", self.get_price())]


class TaxDecorator(ProductDecorator):
    def __init__(self, component, percent=TAX_RATE):
        super().__init__(component)
        self.percent = percent

    def get_price(self):
        price = super().get_price()
        return price + price * self.percent / 100

    def get_steps(self):
        return super().get_steps() + [(f"Tax (VAT) +{self.percent}%", self.get_price())]


class ShippingDecorator(ProductDecorator):
    def __init__(self, component, cost=SHIPPING_COST):
        super().__init__(component)
        self.cost = cost

    def get_price(self):
        return super().get_price() + self.cost

    def get_steps(self):
        return super().get_steps() + [(f"Shipping +{self.cost} ₸", self.get_price())]


def apply_decorators(product, discount=0, tax=False, shipping=False):
    """Wraps the product with the selected decorators, one on top of another."""
    component = product
    if discount > 0:
        component = DiscountDecorator(component, discount)
    if tax:
        component = TaxDecorator(component)
    if shipping:
        component = ShippingDecorator(component)
    return component
