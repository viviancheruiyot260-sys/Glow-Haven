from datetime import datetime

from extensions import db


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    provider = db.Column(db.String(32), default="mpesa", nullable=False)
    status = db.Column(db.String(40), default="pending", nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    checkout_request_id = db.Column(db.String(64), nullable=True, index=True)
    mpesa_receipt = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    order = db.relationship("Order", back_populates="payments")

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "amount": float(self.amount),
            "provider": self.provider,
            "status": self.status,
            "phone": self.phone,
            "checkout_request_id": self.checkout_request_id,
            "mpesa_receipt": self.mpesa_receipt,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
