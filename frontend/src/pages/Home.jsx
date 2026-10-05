import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import ProductCard from "../components/ProductCard";

export default function Home() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/api/products?sort=newest")
      .then((data) => setProducts(data.products.slice(0, 4)))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="home-page">
      <div className="hero-glow hero-glow-a" aria-hidden="true" />
      <div className="hero-glow hero-glow-b" aria-hidden="true" />

      <div className="container">
        <section className="hero">
          <div className="hero-copy">
            <p className="hero-eyebrow">Your beauty. Your glow.</p>
            <h1>
              Discover skincare, makeup &amp; more that <em>love you back</em>.
            </h1>
            <p className="hero-lead">
              Curated beauty essentials for every routine — browse, filter, and checkout securely
              with M-Pesa.
            </p>
            <div className="hero-actions">
              <Link className="btn btn-primary" to="/products">
                Shop the collection
              </Link>
              <Link className="btn btn-ghost" to="/products">
                Browse categories
              </Link>
            </div>
          </div>

          <aside className="hero-card">
            <div className="hero-card-header">
              <div>
                <h2 className="hero-card-title">Featured picks</h2>
                <p className="hero-card-sub">Hand-selected favourites this week</p>
              </div>
              <Link className="hero-card-link" to="/products">
                View all
              </Link>
            </div>

            {error ? (
              <p className="empty-state">{error}</p>
            ) : loading ? (
              <div className="product-grid product-grid-featured" aria-busy="true">
                {[1, 2, 3, 4].map((n) => (
                  <div key={n} className="product-card product-card-skeleton" />
                ))}
              </div>
            ) : (
              <div className="product-grid product-grid-featured">
                {products.map((p) => (
                  <ProductCard key={p.id} product={p} compact />
                ))}
              </div>
            )}
          </aside>
        </section>
      </div>
    </div>
  );
}
