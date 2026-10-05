import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api, formatKes } from "../api";

export default function Orders() {
  const [searchParams] = useSearchParams();
  const highlight = searchParams.get("highlight");
  const [orders, setOrders] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/api/orders")
      .then((data) => setOrders(data.orders))
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return (
      <div className="container" style={{ padding: "2rem 0 4rem" }}>
        <p className="empty-state">{error}</p>
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: "2rem 0 4rem" }}>
      <h1 className="section-title">Your orders</h1>
      {orders.length === 0 ? (
        <p className="empty-state">
          No orders yet. <Link to="/products">Start shopping</Link>
        </p>
      ) : (
        orders.map((order) => (
          <article
            key={order.id}
            className={`summary summary-wide ${String(order.id) === highlight ? "summary-highlight" : ""}`}
          >
            <p>
              <strong>Order #{order.id}</strong> — {order.status.replace("_", " ")}
            </p>
            <p>Total: {formatKes(order.total)}</p>
            <p>Date: {new Date(order.created_at).toLocaleString()}</p>
            {order.mpesa_receipt && <p>Receipt: {order.mpesa_receipt}</p>}
            <ul>
              {order.items.map((i) => (
                <li key={i.id}>
                  {i.quantity} × {i.product.name}
                </li>
              ))}
            </ul>
          </article>
        ))
      )}
    </div>
  );
}
