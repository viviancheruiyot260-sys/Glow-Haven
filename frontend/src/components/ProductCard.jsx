import { Link } from "react-router-dom";
import { formatKes } from "../api";
import ProductImage from "./ProductImage";

export default function ProductCard({ product, showActions = false, compact = false, eagerImage = false }) {
  return (
    <article className={`product-card${compact ? " product-card-compact" : ""}`}>
      <Link to={`/products/${product.id}`} className="product-card-media">
        <ProductImage src={product.image_url} alt={product.name} eager={eagerImage} />
      </Link>
      <div className="product-card-body">
        <span className="badge">{product.category}</span>
        <h3>
          <Link to={`/products/${product.id}`}>{product.name}</Link>
        </h3>
        <span className="price">{formatKes(product.price)}</span>
        {showActions && (
          <Link className="btn btn-outline btn-sm" to={`/products/${product.id}`}>
            View details
          </Link>
        )}
      </div>
    </article>
  );
}
