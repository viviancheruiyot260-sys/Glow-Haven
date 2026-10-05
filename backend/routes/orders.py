from decimal import Decimal

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from extensions import db
from models.order import CartItem, Order, OrderItem

orders_bp = Blueprint("orders", __name__, url_prefix="/api/orders")


@orders_bp.get("")
@jwt_required()
def list_orders():
    user_id = int(get_jwt_identity())
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    return jsonify({"orders": [order.to_dict() for order in orders]})


@orders_bp.get("/<int:order_id>")
@jwt_required()
def get_order(order_id):
    user_id = int(get_jwt_identity())
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order.to_dict())


def create_order_from_cart(user_id: int, phone: str | None = None) -> Order:
    items = CartItem.query.filter_by(user_id=user_id).all()
    if not items:
        raise ValueError("Cart is empty")

    total = Decimal("0")
    for item in items:
        if not item.product or item.product.stock < item.quantity:
            raise ValueError(f"Insufficient stock for {item.product.name if item.product else 'product'}")
        total += Decimal(str(item.product.price)) * item.quantity

    order = Order(user_id=user_id, total=total, status="pending", phone=phone)
    db.session.add(order)
    db.session.flush()

    for item in items:
        db.session.add(
            OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.product.price,
            )
        )

    db.session.commit()
    return order
