import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api, formatKes } from "../api";
import Alert from "../components/Alert";
import ProductImage from "../components/ProductImage";
import { useAuth } from "../context/AuthContext";

export default function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [product, setProduct] = useState(null);
  const [qty, setQty] = useState(1);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    api(`/api/products/${id}`)
      .then(setProduct)
      .catch((err) => setError(err.message));
  }, [id]);

  async function handleAddToCart() {
    if (!isAuthenticated) {
      navigate("/login", { state: { from: `/products/${id}` } });
      return;
    }
    try {
      await api("/api/cart", {
        method: "POST",
        body: JSON.stringify({ product_id: product.id, quantity: Number(qty) }),
      });
      setSuccess("Added to cart!");
      setError("");
      setTimeout(() => setSuccess(""), 4000);
    } catch (err) {
      setError(err.message);
      setSuccess("");
    }
  }

  if (error && !product) {
    return (
      <div className="container">
        <p className="empty-state">{error}</p>
      </div>
    );
  }

  if (!product) return null;

  return (
    <div className="container">
      <Alert type="success" message={success} />
      <Alert type="error" message={error && product ? error : ""} />
      <div className="product-detail">
        <ProductImage src={product.image_url} alt={product.name} eager className="product-detail-img" />
        <div>
          <span className="badge">{product.category}</span>
          <h1 className="section-title">{product.name}</h1>
          <p style={{ color: "var(--muted)", lineHeight: 1.6 }}>{product.description}</p>
          <p className="price" style={{ fontSize: "1.5rem" }}>
            {formatKes(product.price)}
          </p>
          <p>In stock: {product.stock}</p>
          <div className="toolbar" style={{ marginTop: "1.5rem" }}>
            <input
              type="number"
              min="1"
              max={product.stock}
              value={qty}
              onChange={(e) => setQty(e.target.value)}
              style={{ width: 80 }}
            />
            <button className="btn btn-primary" type="button" onClick={handleAddToCart}>
              Add to cart
            </button>
            {success && (
              <Link className="btn btn-outline" to="/cart">
                View cart
              </Link>
            )}
          </div>
          <p style={{ marginTop: "1rem" }}>
            <Link to="/products">← Back to shop</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
