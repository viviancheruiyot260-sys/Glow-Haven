import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import Alert from "../components/Alert";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    phone: "",
    password: "",
  });
  const [error, setError] = useState("");

  function updateField(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      const data = await api("/api/auth/register", {
        method: "POST",
        body: JSON.stringify(form),
      });
      login(data.access_token, data.user);
      navigate("/products");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="container">
      <form className="form-card" onSubmit={handleSubmit}>
        <h1 className="section-title">Create account</h1>
        <Alert message={error} />
        <div className="form-group">
          <label htmlFor="full_name">Full name</label>
          <input
            id="full_name"
            required
            autoComplete="name"
            value={form.full_name}
            onChange={(e) => updateField("full_name", e.target.value)}
          />
        </div>
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            required
            autoComplete="email"
            value={form.email}
            onChange={(e) => updateField("email", e.target.value)}
          />
        </div>
        <div className="form-group">
          <label htmlFor="phone">Phone (M-Pesa)</label>
          <input
            id="phone"
            type="tel"
            placeholder="07XX XXX XXX"
            autoComplete="tel"
            value={form.phone}
            onChange={(e) => updateField("phone", e.target.value)}
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            minLength={6}
            required
            autoComplete="new-password"
            value={form.password}
            onChange={(e) => updateField("password", e.target.value)}
          />
        </div>
        <button className="btn btn-primary" type="submit" style={{ width: "100%" }}>
          Sign up
        </button>
        <p style={{ textAlign: "center", marginTop: "1rem" }}>
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </form>
    </div>
  );
}
