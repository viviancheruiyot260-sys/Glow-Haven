import { useCallback, useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { api, formatKes } from "../api";
import Alert from "../components/Alert";

export default function Cart() {
  const location = useLocation();
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState("");
  const emptyCheckout = location.state?.emptyCheckout;

  const loadCart = useCallback(() => {
    api("/api/cart")
      .then((data) => {
        setItems(data.items);
        setTotal(data.total);
      })
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    loadCart();
  }, [loadCart]);

  async function updateQty(itemId, quantity) {
    try {
      await api(`/api/cart/${itemId}`, {
        method: "PUT",
        body: JSON.stringify({ quantity: Number(quantity) }),
      });
      loadCart();
    } catch (err) {
      setError(err.message);
    }
  }

  async function removeItem(itemId) {
    await api(`/api/cart/${itemId}`, { method: "DELETE" });
    loadCart();
  }

  return (
    <div className="container" style={{ padding: "2rem 0 4rem" }}>
      <h1 className="section-title">Your cart</h1>
      {emptyCheckout && (
        <div className="alert alert-error">Add items to your cart before checkout.</div>
      )}
      <Alert message={error} />
      {!error && items.length === 0 ? (
        <p className="empty-state">
          Your cart is empty. <Link to="/products">Continue shopping</Link>
        </p>
      ) : (
        <>
          <table className="cart-table">
            <thead>
              <tr>
                <th>Product</th>
                <th>Qty</th>
                <th>Subtotal</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td>{item.product?.name ?? "Product"}</td>
                  <td>
                    <input
                      type="number"
                      min="1"
                      value={item.quantity}
                      style={{ width: 70 }}
                      onChange={(e) => updateQty(item.id, e.target.value)}
                    />
                  </td>
                  <td>{formatKes((item.product?.price ?? 0) * item.quantity)}</td>
                  <td>
                    <button className="btn btn-outline" type="button" onClick={() => removeItem(item.id)}>
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="summary">
            <p>
              <strong>Total:</strong> {formatKes(total)}
            </p>
            <Link className="btn btn-primary" to="/checkout" style={{ width: "100%", marginTop: "1rem" }}>
              Checkout with M-Pesa
            </Link>
          </div>
        </>
      )}
    </div>
  );
}
