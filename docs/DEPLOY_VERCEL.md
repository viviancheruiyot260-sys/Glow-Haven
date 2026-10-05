# Deploy Glow Haven on Vercel

Vercel hosts the **React (Vite) storefront**. The **Flask API** must run on a separate Python host (Render, Railway, Fly.io, etc.) because Vercel does not run long-lived Flask apps or SQLite files.

## Architecture

```text
Browser → Vercel (static SPA)  →  HTTPS  →  API host (Flask + MySQL)
              VITE_API_URL
```

## 1. Deploy the API first

### Render (example)

1. Push this repo to GitHub.
2. [Render Dashboard](https://dashboard.render.com/) → **New** → **Blueprint** and connect the repo, or create a **Web Service** manually:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn --chdir backend -w 2 -b 0.0.0.0:$PORT wsgi:application`
3. Add a **MySQL** database (Render, PlanetScale, Railway, etc.) and set environment variables:

| Variable | Required | Notes |
|----------|----------|--------|
| `DATABASE_URI` | Yes | e.g. `mysql+pymysql://user:pass@host:3306/glow_haven?charset=utf8mb4` |
| `SECRET_KEY` | Yes | Random string |
| `JWT_SECRET_KEY` | Yes | Random string |
| `CORS_ORIGINS` | Yes | Your Vercel URL(s), comma-separated, e.g. `https://glow-haven.vercel.app` |
| `MPESA_*` | For real STK | See [MPESA_SANDBOX.md](./MPESA_SANDBOX.md); `MPESA_CALLBACK_URL` must be `https://YOUR-API/api/payments/mpesa/callback` |

4. Open `https://YOUR-API.onrender.com/api/health` — expect `"database_connected": true`.

Do **not** use `USE_SQLITE=1` in production on ephemeral disks; use MySQL (or another managed DB).

## 2. Deploy the frontend on Vercel

1. [vercel.com](https://vercel.com) → **Add New Project** → import your GitHub repo.
2. Vercel should detect settings from the root **`vercel.json`**:
   - **Install:** `npm install --prefix frontend`
   - **Build:** `npm run build --prefix frontend`
   - **Output:** `frontend/dist`
3. **Environment variables** (Project → Settings → Environment Variables):

| Name | Value | Environments |
|------|--------|--------------|
| `VITE_API_URL` | `https://YOUR-API.onrender.com` (no trailing slash) | Production, Preview |

4. Deploy. Visit your `*.vercel.app` URL — shop and featured products should load.

## 3. Post-deploy checks

- [ ] Home page loads products (no “Request failed”).
- [ ] Sign up / log in works (JWT + CORS).
- [ ] `CORS_ORIGINS` includes the exact Vercel origin (scheme + host, no path).
- [ ] M-Pesa callback URL points at the **API** host, not Vercel.

## 4. Custom domain (optional)

- Add the domain in Vercel for the storefront.
- Add the same origin to `CORS_ORIGINS` on the API and redeploy the API.

## Local vs production

| | Local | Vercel |
|---|--------|--------|
| UI | `npm run dev` (5173) | Built static files |
| API | `python app.py` (5000) | External URL in `VITE_API_URL` |
| `/api` proxy | Vite dev proxy | Browser calls API directly |

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| “Request failed” / network error | Set `VITE_API_URL` and redeploy Vercel; ensure API is up. |
| CORS error in browser console | Add your Vercel URL to `CORS_ORIGINS` on the API. |
| 404 on refresh for `/products/1` | Root `vercel.json` SPA rewrite should be committed; redeploy. |
| Build fails on Vercel | Use Node 18+ (see `frontend/package.json` `engines`). |
