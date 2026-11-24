"""Administrator panel: dashboard, products CRUD, categories CRUD, order management."""

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from controllers.helpers import admin_required, order_service
from services.catalog_service import CatalogService

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
catalog = CatalogService()
STATUSES = ["NEW", "PAID", "SHIPPED", "DELIVERED", "CANCELLED"]


@admin_bp.route("/")
@admin_required
def dashboard():
    products = catalog.search()
    return render_template(
        "admin/dashboard.html",
        stats=order_service().stats(),
        product_count=len(products),
        low_stock=[p for p in products if p.stock <= 3],
        recent=order_service().get_all()[:5],
    )


# --- products ----------------------------------------------------------------
@admin_bp.route("/products")
@admin_required
def products():
    return render_template("admin/products.html", products=catalog.search(sort="name"))


@admin_bp.route("/products/add", methods=["GET", "POST"])
@admin_required
def add_product():
    if request.method == "POST":
        try:
            catalog.create_product(request.form)
            flash("Product added.", "success")
            return redirect(url_for("admin.products"))
        except ValueError as error:
            flash(str(error), "error")
    return render_template("admin/product_form.html", product=None,
                           form=request.form, categories=catalog.get_categories())


@admin_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_product(product_id):
    try:
        product = catalog.get_product(product_id)
    except LookupError:
        abort(404)
    if request.method == "POST":
        try:
            catalog.update_product(product_id, request.form)
            flash("Product updated.", "success")
            return redirect(url_for("admin.products"))
        except ValueError as error:
            flash(str(error), "error")
    return render_template("admin/product_form.html", product=product,
                           form=request.form, categories=catalog.get_categories())


@admin_bp.route("/products/<int:product_id>/delete", methods=["POST"])
@admin_required
def delete_product(product_id):
    try:
        catalog.delete_product(product_id)
        flash("Product deleted.", "success")
    except LookupError:
        abort(404)
    except ValueError as error:
        flash(str(error), "error")
    return redirect(url_for("admin.products"))


# --- categories --------------------------------------------------------------
@admin_bp.route("/categories", methods=["GET", "POST"])
@admin_required
def categories():
    if request.method == "POST":
        try:
            catalog.create_category(request.form.get("name"))
            flash("Category added.", "success")
        except ValueError as error:
            flash(str(error), "error")
        return redirect(url_for("admin.categories"))
    return render_template("admin/categories.html", categories=catalog.get_categories())


@admin_bp.route("/categories/<int:category_id>/edit", methods=["POST"])
@admin_required
def edit_category(category_id):
    try:
        catalog.update_category(category_id, request.form.get("name"))
        flash("Category renamed.", "success")
    except LookupError:
        abort(404)
    except ValueError as error:
        flash(str(error), "error")
    return redirect(url_for("admin.categories"))


@admin_bp.route("/categories/<int:category_id>/delete", methods=["POST"])
@admin_required
def delete_category(category_id):
    try:
        catalog.delete_category(category_id)
        flash("Category deleted.", "success")
    except ValueError as error:
        flash(str(error), "error")
    return redirect(url_for("admin.categories"))


# --- orders ------------------------------------------------------------------
@admin_bp.route("/orders")
@admin_required
def orders():
    status = request.args.get("status") or None
    if status and status not in STATUSES:
        status = None
    return render_template("admin/orders.html", orders=order_service().get_all(status),
                           statuses=STATUSES, current=status)


@admin_bp.route("/orders/<int:order_id>/status", methods=["POST"])
@admin_required
def change_status(order_id):
    new_status = request.form.get("status", "")
    try:
        order_service().change_status(order_id, new_status)
        flash(f"Order #{order_id} → {new_status}. Observers notified.", "success")
    except LookupError:
        abort(404)
    except ValueError as error:
        flash(str(error), "error")
    return redirect(request.referrer or url_for("admin.orders"))


@admin_bp.route("/orders/<int:order_id>/delete", methods=["POST"])
@admin_required
def delete_order(order_id):
    try:
        order_service().delete(order_id)
        flash(f"Order #{order_id} deleted.", "success")
    except LookupError:
        abort(404)
    except ValueError as error:
        flash(str(error), "error")
    return redirect(url_for("admin.orders"))
