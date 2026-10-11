from functools import wraps

from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash, abort
)

from database import init_db
from patterns import ProductProxy, OrderFacade

app = Flask(__name__)
app.secret_key = "change-this-demo-secret"

# Demo accounts for the laboratory
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "student": {"password": "student123", "role": "customer"},
}


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper


def product_proxy():
    """Every route works with products only through the Proxy."""
    return ProductProxy(session.get("role", "customer"))


def read_product_form():
    """Returns (name, category, price) or raises ValueError."""
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    price = float(request.form.get("price", ""))
    if not name or not category or price < 0:
        raise ValueError
    return name, category, price


@app.errorhandler(PermissionError)
def permission_denied(error):
    # Raised by ProductProxy when a customer tries an admin-only action
    return render_template("error.html", code=403, message=str(error)), 403


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", code=404, message="Page not found."), 404


# ---------------------------- auth ----------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        user = USERS.get(username)
        if user and user["password"] == password:
            session.clear()
            session["username"] = username
            session["role"] = user["role"]
            return redirect(url_for("products"))
        flash("Invalid username or password.", "error")
    return render_template("base.html", login_page=True)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------------------- products (CRUD) ----------------------------

@app.route("/")
@login_required
def products():
    return render_template("products.html", products=product_proxy().get_all())


@app.route("/products/add", methods=["GET", "POST"])
@login_required
def add_product():
    proxy = product_proxy()
    proxy.check_permission("create")  # block even the GET form for customers

    if request.method == "POST":
        try:
            name, category, price = read_product_form()
        except ValueError:
            flash("Enter valid product details.", "error")
            return redirect(url_for("add_product"))
        proxy.add(name, category, price)
        flash("Product added successfully.")
        return redirect(url_for("products"))

    return render_template("product_form.html", product=None)


@app.route("/products/edit/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    proxy = product_proxy()
    proxy.check_permission("update")

    product = proxy.get(product_id)
    if product is None:
        abort(404)

    if request.method == "POST":
        try:
            name, category, price = read_product_form()
        except ValueError:
            flash("Enter valid product details.", "error")
            return redirect(url_for("edit_product", product_id=product_id))
        proxy.update(product_id, name, category, price)
        flash("Product updated successfully.")
        return redirect(url_for("products"))

    return render_template("product_form.html", product=product)


@app.route("/products/delete/<int:product_id>", methods=["POST"])
@login_required
def delete_product(product_id):
    try:
        product_proxy().delete(product_id)
        flash("Product deleted.")
    except ValueError as error:
        flash(str(error), "error")
    return redirect(url_for("products"))


# ---------------------------- orders ----------------------------

@app.route("/orders")
@login_required
def orders():
    rows = OrderFacade().get_orders(session["username"], session["role"])
    return render_template("orders.html", orders=rows)


@app.route("/orders/add/<int:product_id>", methods=["POST"])
@login_required
def add_order(product_id):
    try:
        quantity = int(request.form.get("quantity", ""))
    except ValueError:
        flash("Quantity must be a whole number.", "error")
        return redirect(url_for("products"))

    try:
        total = OrderFacade().place_order(session["username"], product_id, quantity)
        flash(f"Order placed! Total: ${total:.2f}")
    except ValueError as error:
        flash(str(error), "error")
    return redirect(url_for("products"))


# Create tables and demo products on start (works with "python app.py" and "flask run")
init_db()

if __name__ == "__main__":
    # Port 5000 is taken by AirPlay Receiver on macOS, so we use 5001
    app.run(debug=True, port=5001)
