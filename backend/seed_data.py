from decimal import Decimal

from extensions import db
from models.category import Category
from models.product import Product

CATEGORY_NAMES = ["Skincare", "Makeup", "Haircare", "Fragrances", "Accessories"]

SAMPLE_PRODUCTS = [
    {
        "name": "Radiance Vitamin C Serum",
        "description": "Brightening serum with 15% vitamin C for a luminous, even-toned glow.",
        "price": Decimal("2499.00"),
        "category": "Skincare",
        "image_url": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&auto=format&fit=crop",
        "stock": 40,
    },
    {
        "name": "Velvet Matte Lipstick — Rose",
        "description": "Long-wear matte lipstick in a soft rose shade with a comfortable finish.",
        "price": Decimal("1299.00"),
        "category": "Makeup",
        "image_url": "https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=600&auto=format&fit=crop",
        "stock": 55,
    },
    {
        "name": "Silk Repair Hair Mask",
        "description": "Deep-conditioning mask with argan oil for dry, damaged hair.",
        "price": Decimal("1899.00"),
        "category": "Haircare",
        "image_url": "https://images.pexels.com/photos/3785147/pexels-photo-3785147.jpeg?auto=compress&cs=tinysrgb&w=600",
        "stock": 30,
    },
    {
        "name": "Bloom Eau de Parfum",
        "description": "Floral fragrance with notes of peony, jasmine, and warm amber.",
        "price": Decimal("4599.00"),
        "category": "Fragrances",
        "image_url": "https://images.unsplash.com/photo-1541643600914-78b084683601?w=600&auto=format&fit=crop",
        "stock": 20,
    },
    {
        "name": "Luxe Makeup Brush Set",
        "description": "Five-piece synthetic brush set for seamless blending and application.",
        "price": Decimal("2199.00"),
        "category": "Accessories",
        "image_url": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=600&auto=format&fit=crop",
        "stock": 25,
    },
    {
        "name": "Hydra Glow Moisturizer",
        "description": "Lightweight daily moisturizer with hyaluronic acid and SPF 15.",
        "price": Decimal("1999.00"),
        "category": "Skincare",
        "image_url": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&auto=format&fit=crop",
        "stock": 45,
    },
    {
        "name": "Cloud Setting Powder",
        "description": "Translucent setting powder that blurs pores and controls shine.",
        "price": Decimal("1599.00"),
        "category": "Makeup",
        "image_url": "https://images.pexels.com/photos/6634644/pexels-photo-6634644.jpeg?auto=compress&cs=tinysrgb&w=600",
        "stock": 35,
    },
    {
        "name": "Curl Define Styling Cream",
        "description": "Defines curls and coils without crunch for soft, bouncy hair.",
        "price": Decimal("1399.00"),
        "category": "Haircare",
        "image_url": "https://images.pexels.com/photos/4465124/pexels-photo-4465124.jpeg?auto=compress&cs=tinysrgb&w=600",
        "stock": 28,
    },
]


def _slugify(name: str) -> str:
    return name.strip().lower().replace(" ", "-")


def seed_categories_if_empty():
    if Category.query.count() > 0:
        return
    for name in CATEGORY_NAMES:
        db.session.add(Category(name=name, slug=_slugify(name)))
    db.session.commit()


def seed_products_if_empty():
    seed_categories_if_empty()
    if Product.query.count() > 0:
        return

    categories = {cat.name: cat.id for cat in Category.query.all()}
    for item in SAMPLE_PRODUCTS:
        db.session.add(
            Product(
                category_id=categories[item["category"]],
                name=item["name"],
                description=item["description"],
                price=item["price"],
                image_url=item["image_url"],
                stock=item["stock"],
            )
        )
    db.session.commit()


PRODUCT_IMAGE_URL_FIXES = {item["name"]: item["image_url"] for item in SAMPLE_PRODUCTS}


def sync_product_image_urls():
    updated = False
    for name, url in PRODUCT_IMAGE_URL_FIXES.items():
        product = Product.query.filter_by(name=name).first()
        if product and product.image_url != url:
            product.image_url = url
            updated = True
    if updated:
        db.session.commit()
