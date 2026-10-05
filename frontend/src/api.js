const rawBase = import.meta.env.VITE_API_URL || "";
const API_BASE = rawBase.replace(/\/$/, "");
const IS_DEV = import.meta.env.DEV;

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

  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  } catch {
    throw new Error(
      IS_DEV
        ? "Cannot reach the API. Start the backend: cd backend && python app.py"
        : "Cannot reach the API. Check VITE_API_URL on Vercel and that the API host is running."
    );
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const serverMsg = data.error || data.msg || data.message;
    if (!serverMsg && response.status >= 502) {
      throw new Error(
        IS_DEV
          ? "API server is not running. In a second terminal: cd backend && python app.py"
          : "API server unavailable. Verify your deployed backend and VITE_API_URL."
      );
    }
    throw new Error(serverMsg || "Request failed");
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
