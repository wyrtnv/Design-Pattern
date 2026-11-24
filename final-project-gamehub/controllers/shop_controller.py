"""Catalog, product page, cart and checkout (customer side)."""

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from controllers.helpers import cart, current_user, login_required, order_service, parse_int
from patterns.delivery_strategy import DeliveryContext
from patterns.payment_factory import PaymentFactory
from services.catalog_service import CatalogService

shop_bp = Blueprint("shop", __name__)
catalog_service = CatalogService()


@shop_bp.route("/")
def catalog():
    text = request.args.get("q", "")
    category_id = parse_int(request.args.get("category"))
    sort = request.args.get("sort", "new")
    return render_template(
        "catalog.html",
        products=catalog_service.search(text, category_id, sort),
        categories=catalog_service.get_categories(),
        q=text, category_id=category_id, sort=sort,
    )


@shop_bp.route("/product/<int:product_id>")
def product(product_id):
    try:
        item = catalog_service.get_product(product_id)
    except LookupError:
        abort(404)
    return render_template("product.html", product=item)


# --- cart --------------------------------------------------------------------
@shop_bp.route("/cart")
def view_cart():
    service = cart()
    items = service.items()
    subtotal = sum(i.line_total for i in items)
    return render_template("cart.html", items=items, subtotal=subtotal)


@shop_bp.route("/cart/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    quantity = parse_int(request.form.get("quantity"), 1)
    try:
        product_obj = cart().add(product_id, quantity)
        flash(f"{product_obj.name} added to cart.", "success")
    except (ValueError, LookupError) as error:
        flash(str(error), "error")
    return redirect(request.referrer or url_for("shop.catalog"))


@shop_bp.route("/cart/update/<int:product_id>", methods=["POST"])
def update_cart(product_id):
    try:
        cart().set_quantity(product_id, parse_int(request.form.get("quantity"), 0))
    except ValueError as error:
        flash(str(error), "error")
    return redirect(url_for("shop.view_cart"))


@shop_bp.route("/cart/remove/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart().remove(product_id)
    flash("Item removed from cart.", "success")
    return redirect(url_for("shop.view_cart"))


# --- checkout ----------------------------------------------------------------
@shop_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    service = cart()
    items = service.items()
    if not items:
        flash("Your cart is empty.", "error")
        return redirect(url_for("shop.catalog"))

    orders = order_service()
    form = request.form if request.method == "POST" else {}
    delivery_code = form.get("delivery", "courier")
    quotes = {s.code: orders.quote(items, s.code) for s in DeliveryContext.all_strategies()}

    if request.method == "POST":
        try:
            order = orders.checkout(current_user(), items, delivery_code,
                                    form.get("payment", ""), form.get("address", ""))
        except (ValueError, LookupError) as error:
            flash(str(error), "error")
        else:
            service.clear()
            flash(f"Order #{order.id} placed and paid. Thank you!", "success")
            return redirect(url_for("orders.detail", order_id=order.id))

    return render_template(
        "checkout.html", items=items, quotes=quotes,
        strategies=DeliveryContext.all_strategies(), payments=PaymentFactory.available(),
        selected_delivery=delivery_code, selected_payment=form.get("payment", "card"),
        address=form.get("address", ""),
    )
