# Deploy Glow Haven on Vercel (Services)

This repo uses Vercel **Services**: one project, two services, one domain.

| Service | Role | Public? |
|---------|------|---------|
| `frontend` | Vite React storefront (`frontend/dist`) | Yes — `/` and client routes |
| `glow-haven-api` | Flask API (`backend/app.py`) | Yes — only via `/api/*` rewrites |

Routing is defined in root **`vercel.json`**. The API service is **internal by default**; top-level rewrites expose it at `/api/...`.

## Architecture

```text
Browser → https://your-app.vercel.app
            ├─ /api/*     → glow-haven-api (Flask)
            └─ /*         → frontend (static SPA)
```

The browser calls **same-origin** `/api/...` (leave **`VITE_API_URL` unset** on Vercel). No service **bindings** are required — the React app runs in the browser, not in a serverless function.

## 1. Import on Vercel

1. [vercel.com](https://vercel.com) → **New Project** → import `viviancheruiyot260-sys/Glow-Haven`.
2. Choose **Import multi-service project** (or set **Framework Preset** to **Services** in project settings).
3. Root directory: **`./`** (repo root — `vercel.json` lives here).
4. Deploy.

## 2. Environment variables (project settings)

Set these for **Production** (and Preview if you use it):

| Variable | Service | Required | Notes |
|----------|---------|----------|--------|
| `DATABASE_URI` | API | **Yes** | MySQL (or compatible). Do **not** rely on `USE_SQLITE=1` on Vercel — the filesystem is ephemeral. |
| `SECRET_KEY` | API | **Yes** | Random string |
| `JWT_SECRET_KEY` | API | **Yes** | Random string |
| `MPESA_*` | API | For STK | See [MPESA_SANDBOX.md](./MPESA_SANDBOX.md) |
| `MPESA_CALLBACK_URL` | API | For STK | `https://YOUR-VERCEL-DOMAIN/api/payments/mpesa/callback` |
| `VITE_API_URL` | Frontend | **Leave empty** | Same-origin `/api` routing; only set if API is hosted elsewhere |

`CORS_ORIGINS` can stay `*` or list your Vercel URL when using same-origin `/api` (no CORS preflight for simple same-origin GETs; credentialed cross-origin not used).

## 3. Post-deploy checks

- [ ] `https://YOUR-APP.vercel.app/api/health` → `"database_connected": true`
- [ ] Home page loads featured products
- [ ] Sign up / log in / cart / checkout
- [ ] M-Pesa callback URL uses your **Vercel** domain + `/api/payments/mpesa/callback`

## 4. Local development

| | Command |
|---|--------|
| API | `cd backend && python app.py` |
| UI | `cd frontend && npm run dev` (proxies `/api` → `:5000`) |

Optional: `vercel dev` at repo root runs all services together (requires [Vercel CLI](https://vercel.com/docs/cli)).

## Alternative: API on Render

You can still host only the **frontend** on Vercel (legacy single-service build) and point `VITE_API_URL` at Render — see [render.yaml](../render.yaml). The committed **`vercel.json` services** layout is the recommended single-domain setup.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| “Import multi-service… needs vercel.json” | Pull latest `main`; ensure `services` key exists. |
| “Request failed” on home | Check `/api/health`; set `DATABASE_URI`; redeploy API service. |
| 404 on `/products/1` refresh | Redeploy; confirm frontend service + catch-all rewrite. |
| Build: Flask not found | `entrypoint` is `app:app` in `backend/`; see `backend/pyproject.toml`. |
