import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import ProductCard from "../components/ProductCard";

export default function Products() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [sort, setSort] = useState("newest");
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [error, setError] = useState("");

  const loadProducts = useCallback(() => {
    const params = new URLSearchParams({ search, category, sort });
    api(`/api/products?${params}`)
      .then((data) => {
        setProducts(data.products);
        setCategories((prev) => (prev.length ? prev : data.categories));
      })
      .catch((err) => setError(err.message));
  }, [search, category, sort]);

  useEffect(() => {
    loadProducts();
  }, [loadProducts]);

  return (
    <div className="container" style={{ padding: "2rem 0 4rem" }}>
      <h1 className="section-title">All products</h1>
      <div className="toolbar">
        <input
          type="search"
          placeholder="Search products..."
          aria-label="Search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select aria-label="Category" value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="">All categories</option>
          {categories.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
        <select aria-label="Sort" value={sort} onChange={(e) => setSort(e.target.value)}>
          <option value="newest">Newest</option>
          <option value="price_asc">Price: low to high</option>
          <option value="price_desc">Price: high to low</option>
          <option value="name_asc">Name A–Z</option>
        </select>
      </div>
      {error ? (
        <p className="empty-state">{error}</p>
      ) : products.length === 0 ? (
        <p className="empty-state">No products match your filters.</p>
      ) : (
        <div className="product-grid">
          {products.map((p) => (
            <ProductCard key={p.id} product={p} showActions />
          ))}
        </div>
      )}
    </div>
  );
}
