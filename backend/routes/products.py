from flask import Blueprint, jsonify, request
from sqlalchemy import func, or_

from models.category import Category
from models.product import Product

products_bp = Blueprint("products", __name__, url_prefix="/api/products")

SORT_OPTIONS = {
    "price_asc": Product.price.asc(),
    "price_desc": Product.price.desc(),
    "name_asc": Product.name.asc(),
    "newest": Product.created_at.desc(),
}


@products_bp.get("")
def list_products():
    search = (request.args.get("search") or "").strip()
    category = (request.args.get("category") or "").strip()
    sort = request.args.get("sort") or "newest"

    query = Product.query.join(Category)
    if search:
        like = f"%{search.lower()}%"
        query = query.filter(
            or_(
                func.lower(Product.name).like(like),
                func.lower(Product.description).like(like),
            )
        )
    if category:
        query = query.filter(Category.name == category)

    order = SORT_OPTIONS.get(sort, SORT_OPTIONS["newest"])
    products = query.order_by(order).all()
    categories = [row.name for row in Category.query.order_by(Category.name).all()]
    return jsonify({"products": [p.to_dict() for p in products], "categories": categories})


@products_bp.get("/<int:product_id>")
def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product.to_dict())
