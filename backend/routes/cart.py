from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from extensions import db
from models.order import CartItem
from models.product import Product

cart_bp = Blueprint("cart", __name__, url_prefix="/api/cart")


def _cart_total(items):
    return sum(float(item.product.price) * item.quantity for item in items if item.product)


@cart_bp.get("")
@jwt_required()
def get_cart():
    user_id = int(get_jwt_identity())
    items = CartItem.query.filter_by(user_id=user_id).all()
    return jsonify({"items": [item.to_dict() for item in items], "total": _cart_total(items)})


@cart_bp.post("")
@jwt_required()
def add_to_cart():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    product_id = data.get("product_id")
    quantity = int(data.get("quantity") or 1)

    if not product_id or quantity < 1:
        return jsonify({"error": "Valid product_id and quantity are required"}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    if product.stock < quantity:
        return jsonify({"error": "Insufficient stock"}), 400

    item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if item:
        new_qty = item.quantity + quantity
        if new_qty > product.stock:
            return jsonify({"error": "Insufficient stock"}), 400
        item.quantity = new_qty
    else:
        item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(item)

    db.session.commit()
    items = CartItem.query.filter_by(user_id=user_id).all()
    return jsonify({"items": [i.to_dict() for i in items], "total": _cart_total(items)})


@cart_bp.put("/<int:item_id>")
@jwt_required()
def update_cart_item(item_id):
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    quantity = int(data.get("quantity") or 0)

    item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
    if not item:
        return jsonify({"error": "Cart item not found"}), 404
    if quantity < 1:
        return jsonify({"error": "Quantity must be at least 1"}), 400
    if item.product.stock < quantity:
        return jsonify({"error": "Insufficient stock"}), 400

    item.quantity = quantity
    db.session.commit()
    items = CartItem.query.filter_by(user_id=user_id).all()
    return jsonify({"items": [i.to_dict() for i in items], "total": _cart_total(items)})


@cart_bp.delete("/<int:item_id>")
@jwt_required()
def remove_cart_item(item_id):
    user_id = int(get_jwt_identity())
    item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
    if not item:
        return jsonify({"error": "Cart item not found"}), 404

    db.session.delete(item)
    db.session.commit()
    items = CartItem.query.filter_by(user_id=user_id).all()
    return jsonify({"items": [i.to_dict() for i in items], "total": _cart_total(items)})
