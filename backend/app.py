import sys

from pathlib import Path



from flask import Flask, jsonify, send_from_directory

from flask_cors import CORS

from sqlalchemy import text



BACKEND_DIR = Path(__file__).resolve().parent

if str(BACKEND_DIR) not in sys.path:

    sys.path.insert(0, str(BACKEND_DIR))



from config import Config  # noqa: E402

from db_startup import run_startup_diagnostics  # noqa: E402

from extensions import db, jwt  # noqa: E402

from models import (  # noqa: E402,F401

    CartItem,

    Category,

    Order,

    OrderItem,

    Payment,

    Product,

    User,

)

from routes.auth import auth_bp  # noqa: E402

from routes.cart import cart_bp  # noqa: E402

from routes.orders import orders_bp  # noqa: E402

from routes.payments import payments_bp  # noqa: E402

from routes.products import products_bp  # noqa: E402

from seed_data import seed_products_if_empty, sync_product_image_urls  # noqa: E402





def create_app():

    frontend_dist = Config.FRONTEND_DIR

    app = Flask(__name__, static_folder=str(frontend_dist), static_url_path="")

    app.config.from_object(Config)



    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)

    jwt.init_app(app)

    @jwt.unauthorized_loader
    def jwt_unauthorized(reason):
        return jsonify({"error": "Please log in to continue."}), 401

    @jwt.invalid_token_loader
    def jwt_invalid_token(reason):
        return jsonify({"error": "Session expired. Please log in again."}), 401

    app.register_blueprint(auth_bp)

    app.register_blueprint(products_bp)

    app.register_blueprint(cart_bp)

    app.register_blueprint(orders_bp)

    app.register_blueprint(payments_bp)



    @app.get("/api/health")

    def health():

        db_ok = False

        try:

            with db.engine.connect() as connection:

                connection.execute(text("SELECT 1"))

            db_ok = True

        except Exception:

            db_ok = False



        return jsonify(

            {

                "status": "ok" if db_ok else "degraded",

                "name": "Glow Haven API",

                "database": Config.database_backend(),

                "database_connected": db_ok,

            }

        )



    @app.route("/", defaults={"path": ""})

    @app.route("/<path:path>")

    def spa(path):

        if not frontend_dist.is_dir():

            return (

                jsonify(

                    {

                        "error": "Frontend not built. Run: cd frontend && npm install && npm run build"

                    }

                ),

                503,

            )



        if path.startswith("assets/") or path.endswith(

            (".js", ".css", ".map", ".ico", ".png", ".jpg", ".svg", ".webp")

        ):

            file_path = frontend_dist / path

            if file_path.is_file():

                return send_from_directory(frontend_dist, path)



        index_path = frontend_dist / "index.html"

        if index_path.is_file():

            return send_from_directory(frontend_dist, "index.html")



        return jsonify({"error": "Frontend build missing index.html"}), 503



    with app.app_context():

        db.create_all()

        seed_products_if_empty()
        sync_product_image_urls()



    return app





app = create_app()





if __name__ == "__main__":

    import sys



    run_startup_diagnostics(app)

    ok_prefix = "✓" if "utf" in (sys.stdout.encoding or "").lower() else "[OK]"

    print(f"{ok_prefix} Glow Haven backend running")

    app.run(host="0.0.0.0", port=5000, debug=True)


