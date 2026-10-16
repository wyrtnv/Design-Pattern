from datetime import datetime

from database import db


class PaymentLog(db.Model):
    __tablename__ = "payment_logs"

    id = db.Column(db.Integer, primary_key=True)
    payment_method = db.Column(db.String(50), nullable=False)
    payer = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    fee = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="SUCCESS")
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "method": self.payment_method,
            "payer": self.payer,
            "amount": self.amount,
            "fee": self.fee,
            "total": self.total,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
