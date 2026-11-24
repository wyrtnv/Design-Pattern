from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)
auth = AuthService()


def _safe_next(target):
    # Only local paths: prevents an open redirect to another site.
    return target if target and target.startswith("/") and not target.startswith("//") else None


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            user = auth.login(request.form.get("username", ""), request.form.get("password", ""))
        except ValueError as error:
            flash(str(error), "error")
            return render_template("login.html"), 401
        cart = session.get("cart", {})
        session.clear()
        session["user_id"] = user.id
        session["cart"] = cart
        flash(f"Welcome, {user.full_name}!", "success")
        return redirect(_safe_next(request.args.get("next")) or url_for("shop.catalog"))
    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        form = request.form
        if form.get("password") != form.get("confirm"):
            flash("Passwords do not match.", "error")
            return render_template("register.html"), 400
        try:
            user_id = auth.register(form.get("username", ""), form.get("password", ""),
                                    form.get("full_name", ""))
        except ValueError as error:
            flash(str(error), "error")
            return render_template("register.html"), 400
        session.clear()
        session["user_id"] = user_id
        flash("Account created. Happy shopping!", "success")
        return redirect(url_for("shop.catalog"))
    return render_template("register.html")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("shop.catalog"))
