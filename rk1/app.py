from flask import Flask, render_template, request, redirect, url_for, flash, abort

import database as db
from patterns.decorators import Product, apply_decorators, TAX_RATE, SHIPPING_COST

app = Flask(__name__)
app.secret_key = "change-this-demo-secret"

CATEGORIES = ["Electronics", "Clothing", "Books", "Home", "Sport", "Other"]


def to_product(row):
    """DB row -> Product object (the component that decorators wrap)."""
    return Product(row["id"], row["name"], row["price"], row["category"])


def decorate(row):
    """Applies the decorators saved for this product in the database."""
    return apply_decorators(
        to_product(row),
        discount=row["discount"],
        tax=bool(row["apply_tax"]),
        shipping=bool(row["apply_shipping"]),
    )


def read_product_form():
    """Reads and validates the form. Returns (data, errors)."""
    form = request.form
    data = {
        "name": form.get("name", "").strip(),
        "category": form.get("category", "").strip(),
        "price": form.get("price", "").strip(),
        "discount": form.get("discount", "0").strip() or "0",
        "apply_tax": 1 if form.get("apply_tax") else 0,
        "apply_shipping": 1 if form.get("apply_shipping") else 0,
    }
    errors = []

    if not data["name"]:
        errors.append("Name is required.")
    elif len(data["name"]) > 100:
        errors.append("Name must be at most 100 characters.")

    if data["category"] not in CATEGORIES:
        errors.append("Choose a category from the list.")

    try:
        data["price"] = float(data["price"])
        if data["price"] <= 0:
            errors.append("Price must be greater than 0.")
    except ValueError:
        errors.append("Price must be a number.")

    try:
        data["discount"] = int(data["discount"])
        if not 0 <= data["discount"] <= 90:
            errors.append("Discount must be between 0 and 90%.")
    except ValueError:
        errors.append("Discount must be a whole number.")

    return data, errors


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", message="Product not found."), 404


@app.template_filter("money")
def money(value):
    return f"{value:,.0f} ₸".replace(",", " ")


@app.template_filter("plain")
def plain(value):
    """450000.0 -> 450000 for form inputs; invalid input is shown as typed."""
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


# ---------------------------- Read ----------------------------

@app.route("/")
def index():
    products = [(row, decorate(row)) for row in db.get_all_products()]
    return render_template("index.html", products=products)


@app.route("/product/<int:product_id>")
def detail(product_id):
    """Pattern demo: decorators can be switched on/off live via checkboxes."""
    row = db.get_product(product_id)
    if row is None:
        abort(404)

    # If the demo form was submitted use its values, otherwise the saved ones
    if "demo" in request.args:
        try:
            discount = max(0, min(90, int(request.args.get("discount", 0))))
        except ValueError:
            discount = 0
        tax = "tax" in request.args
        shipping = "shipping" in request.args
    else:
        discount = row["discount"]
        tax = bool(row["apply_tax"])
        shipping = bool(row["apply_shipping"])

    component = apply_decorators(to_product(row), discount, tax, shipping)

    # Chain of class names, e.g. ShippingDecorator(TaxDecorator(Product))
    chain = []
    current = component
    while hasattr(current, "_component"):
        chain.append(type(current).__name__)
        current = current._component
    chain.append("Product")

    return render_template(
        "detail.html", product=row, component=component, chain=chain,
        discount=discount, tax=tax, shipping=shipping,
        tax_rate=TAX_RATE, shipping_cost=SHIPPING_COST,
    )


# ---------------------------- Create ----------------------------

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        data, errors = read_product_form()
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("add.html", product=data, categories=CATEGORIES), 400
        db.add_product(data)
        flash(f"Product “{data['name']}” added.")
        return redirect(url_for("index"))

    return render_template("add.html", product=None, categories=CATEGORIES)


# ---------------------------- Update ----------------------------

@app.route("/edit/<int:product_id>", methods=["GET", "POST"])
def edit(product_id):
    row = db.get_product(product_id)
    if row is None:
        abort(404)

    if request.method == "POST":
        data, errors = read_product_form()
        if errors:
            for error in errors:
                flash(error, "error")
            data["id"] = product_id
            return render_template("edit.html", product=data, categories=CATEGORIES), 400
        db.update_product(product_id, data)
        flash(f"Product “{data['name']}” updated.")
        return redirect(url_for("index"))

    return render_template("edit.html", product=row, categories=CATEGORIES)


# ---------------------------- Delete ----------------------------

@app.route("/delete/<int:product_id>", methods=["POST"])
def delete(product_id):
    row = db.get_product(product_id)
    if row is None:
        abort(404)
    db.delete_product(product_id)
    flash(f"Product “{row['name']}” deleted.")
    return redirect(url_for("index"))


# Create the table and demo products on start
db.init_db()

if __name__ == "__main__":
    # Port 5000 is taken by AirPlay Receiver on macOS, so we use 5002
    app.run(debug=True, port=5002)
