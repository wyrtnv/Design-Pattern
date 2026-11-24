import math
import os

from flask import Flask, request, jsonify, render_template

from database import DatabaseManager, db
from models import PaymentLog
from factory import PaymentFactory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "app_database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize DB via Singleton
db_manager = DatabaseManager(app)


@app.route("/")
def index():
    """Small HTML page to test the API from the browser."""
    return render_template("index.html")


@app.route("/api/pay", methods=["POST"])
def make_payment():
    data = request.get_json(silent=True)

    if not data or not all(k in data for k in ("method", "payer", "amount")):
        return jsonify({"error": "Missing required fields: method, payer, amount"}), 400

    payer = str(data["payer"]).strip()
    if not payer:
        return jsonify({"error": "Payer must not be empty"}), 400

    try:
        amount = float(data["amount"])
    except (TypeError, ValueError):
        return jsonify({"error": "Amount must be a number"}), 400
    if not math.isfinite(amount) or amount <= 0:
        return jsonify({"error": "Amount must be greater than 0"}), 400

    try:
        # 1. Obtain service instance via Factory
        service = PaymentFactory.create_payment_service(data["method"])

        # 2. Execute business logic (polymorphism: each service pays differently)
        result_message = service.pay(payer, amount)
        fee = service.calculate_fee(amount)

        # 3. Persist transaction in SQLite
        log_entry = PaymentLog(
            payment_method=service.name,
            payer=payer,
            amount=amount,
            fee=fee,
            total=round(amount + fee, 2),
            status="SUCCESS",
        )
        db.session.add(log_entry)
        db.session.commit()

        return jsonify({
            "status": "success",
            "service_class": type(service).__name__,
            "message": result_message,
            "log": log_entry.to_dict(),
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Server error: {e}"}), 500


@app.route("/api/payments", methods=["GET"])
def get_payments():
    """History of all payments, newest first. Optional filter: ?method=paypal"""
    query = PaymentLog.query
    method = request.args.get("method")
    if method:
        query = query.filter_by(payment_method=method.lower())
    logs = query.order_by(PaymentLog.created_at.desc()).all()
    return jsonify([log.to_dict() for log in logs]), 200


@app.route("/api/payments/<int:payment_id>", methods=["GET"])
def get_payment(payment_id):
    log = db.session.get(PaymentLog, payment_id)
    if log is None:
        return jsonify({"error": f"Payment {payment_id} not found"}), 404
    return jsonify(log.to_dict()), 200


@app.route("/api/singleton-check", methods=["GET"])
def singleton_check():
    """Proof of Singleton: every DatabaseManager() is the same object."""
    a = DatabaseManager()
    b = DatabaseManager()
    return jsonify({
        "same_object": a is b and a is db_manager,
        "id_first_call": id(a),
        "id_second_call": id(b),
        "id_app_db_manager": id(db_manager),
    }), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405


if __name__ == "__main__":
    # Port 5000 is taken by AirPlay Receiver on macOS, so we use 5003
    app.run(debug=True, port=5003)
