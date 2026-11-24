"""Customer orders and notification inbox."""

from flask import Blueprint, abort, flash, redirect, render_template, url_for

from controllers.helpers import current_user, login_required, order_service
from repositories.repositories import NotificationRepository

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")
notifications = NotificationRepository()


@orders_bp.route("/")
@login_required
def my_orders():
    return render_template("orders.html", orders=order_service().get_for_user(current_user()))


@orders_bp.route("/<int:order_id>")
@login_required
def detail(order_id):
    try:
        order = order_service().get(order_id, current_user())
    except LookupError:
        abort(404)
    return render_template("order_detail.html", order=order)


@orders_bp.route("/<int:order_id>/cancel", methods=["POST"])
@login_required
def cancel(order_id):
    service = order_service()
    try:
        order = service.get(order_id, current_user())
        service.cancel(order)
        flash(f"Order #{order_id} cancelled.", "success")
    except LookupError:
        abort(404)
    except ValueError as error:
        flash(str(error), "error")
    return redirect(url_for("orders.detail", order_id=order_id))


@orders_bp.route("/notifications")
@login_required
def inbox():
    user = current_user()
    items = notifications.for_user(user.id)
    notifications.mark_all_read(user.id)
    return render_template("notifications.html", notifications=items)
