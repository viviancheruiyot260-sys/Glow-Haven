import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, formatKes } from "../api";
import Alert from "../components/Alert";
import { useAuth } from "../context/AuthContext";

const POLL_MS = 3000;
const POLL_MAX = 40;

export default function Checkout() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const pollRef = useRef(null);
  const [phone, setPhone] = useState(user?.phone || "");
  const [total, setTotal] = useState(0);
  const [itemCount, setItemCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [awaitingMpesa, setAwaitingMpesa] = useState(false);
  const [mpesaConfig, setMpesaConfig] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api("/api/payments/mpesa/config")
      .then(setMpesaConfig)
      .catch(() => setMpesaConfig({ configured: false, env: "sandbox" }));
  }, []);

  useEffect(() => {
    api("/api/cart")
      .then((data) => {
        setTotal(data.total);
        setItemCount(data.items.length);
        if (data.items.length === 0 && !awaitingMpesa) {
          navigate("/cart", { replace: true, state: { emptyCheckout: true } });
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [navigate, awaitingMpesa]);

  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  function stopPolling() {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }

  async function pollPaymentStatus(orderId) {
    let attempts = 0;
    stopPolling();

    pollRef.current = setInterval(async () => {
      attempts += 1;
      try {
        await api(`/api/payments/mpesa/query/${orderId}`, { method: "POST" });
        const order = await api(`/api/payments/mpesa/status/${orderId}`);

        if (order.status === "paid") {
          stopPolling();
          setAwaitingMpesa(false);
          setMessage("Payment received. Thank you!");
          setTimeout(() => navigate(`/orders?highlight=${orderId}`), 800);
          return;
        }
        if (order.status === "failed") {
          stopPolling();
          setAwaitingMpesa(false);
          setError("M-Pesa payment failed or was cancelled.");
          return;
        }
      } catch {
        /* keep polling until timeout */
      }

      if (attempts >= POLL_MAX) {
        stopPolling();
        setAwaitingMpesa(false);
        setError(
          "Payment still pending. If you completed STK on your phone, check Orders in a moment."
        );
        navigate(`/orders?highlight=${orderId}`);
      }
    }, POLL_MS);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (itemCount === 0 || total <= 0) {
      setError("Your cart is empty. Add products before checkout.");
      return;
    }
    setSubmitting(true);
    setError("");
    setMessage("");
    try {
      const result = await api("/api/payments/mpesa/stk-push", {
        method: "POST",
        body: JSON.stringify({ phone }),
      });

      if (result.mock) {
        setMessage(result.message);
        setTimeout(() => navigate(`/orders?highlight=${result.order.id}`), 1200);
        return;
      }

      setAwaitingMpesa(true);
      setMessage(
        result.message || "STK push sent. Enter your M-Pesa PIN on your phone to complete payment."
      );
      pollPaymentStatus(result.order.id);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <div className="container" style={{ padding: "2rem 0 4rem" }}>
        <p className="empty-state">Loading checkout…</p>
      </div>
    );
  }

  const sandboxHint = mpesaConfig?.env === "sandbox" && mpesaConfig?.configured;

  return (
    <div className="container" style={{ padding: "2rem 0 4rem" }}>
      <h1 className="section-title">M-Pesa checkout</h1>
      <Alert type="success" message={message} />
      <Alert message={error} />
      <div className="form-card checkout-card">
        <p style={{ color: "var(--muted)" }}>
          Order total: {formatKes(total)} ({itemCount} item{itemCount === 1 ? "" : "s"})
        </p>

        {mpesaConfig?.configured ? (
          <p className="checkout-mode">
            Daraja <strong>{mpesaConfig.env}</strong>
            {mpesaConfig.shortcode ? ` · Paybill ${mpesaConfig.shortcode}` : ""}
          </p>
        ) : mpesaConfig?.partial_credentials ? (
          <p className="checkout-mode checkout-mode-warn">
            STK push blocked: add{" "}
            <strong>{(mpesaConfig.missing || []).join(", ")}</strong> in <code>.env</code> (see{" "}
            <code>docs/MPESA_SANDBOX.md</code>).
          </p>
        ) : (
          <p className="checkout-mode checkout-mode-mock">
            Daraja not configured — mock checkout (add keys in <code>.env</code> for sandbox STK).
          </p>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="phone">M-Pesa phone number</label>
            <input
              id="phone"
              type="tel"
              required
              placeholder="2547XXXXXXXX or 07XXXXXXXX"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              disabled={awaitingMpesa}
            />
            {sandboxHint && (
              <span className="field-hint">
                Sandbox test number: <strong>{mpesaConfig.sandbox_test_msisdn}</strong> (Safaricom
                docs)
              </span>
            )}
          </div>
          <button
            className="btn btn-primary"
            type="submit"
            style={{ width: "100%" }}
            disabled={submitting || awaitingMpesa || itemCount === 0}
          >
            {awaitingMpesa
              ? "Waiting for M-Pesa…"
              : submitting
                ? "Sending STK push…"
                : "Pay with M-Pesa"}
          </button>
        </form>

        {awaitingMpesa && (
          <p className="checkout-wait">Complete the prompt on your phone. This page will update automatically.</p>
        )}

        <p style={{ marginTop: "1rem" }}>
          <Link to="/cart">← Back to cart</Link>
        </p>
      </div>
    </div>
  );
}
