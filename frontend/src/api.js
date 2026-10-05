const API_BASE = import.meta.env.VITE_API_URL || "";

export function getToken() {
  return localStorage.getItem("gh_token");
}

export function setSession(token, user) {
  localStorage.setItem("gh_token", token);
  localStorage.setItem("gh_user", JSON.stringify(user));
}

export function clearSession() {
  localStorage.removeItem("gh_token");
  localStorage.removeItem("gh_user");
}

export function getStoredUser() {
  const raw = localStorage.getItem("gh_user");
  return raw ? JSON.parse(raw) : null;
}

export async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || data.msg || data.message || "Request failed");
  }
  return data;
}

export function formatKes(amount) {
  return new Intl.NumberFormat("en-KE", {
    style: "currency",
    currency: "KES",
    maximumFractionDigits: 0,
  }).format(amount);
}
