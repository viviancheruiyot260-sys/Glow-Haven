# Deploy Glow Haven on Vercel (Services)

Confirmed architecture (multi-service, single domain):

| Service | Root | Framework | Public routing |
|---------|------|-----------|----------------|
| `frontend` | `frontend/` | Vite → `dist/` | `/` and all non-API paths (SPA) |
| `glow-haven-api` | `backend/` | Flask `app:app` | `/api/*` only (via top-level rewrites) |

**Bindings:** none — browser uses same-origin `/api/...`. **Do not set `VITE_API_URL`** on Vercel unless the API is hosted elsewhere.

Configuration lives in root [`vercel.json`](../vercel.json).

> **Note:** Do not list `backend/` in `.vercelignore` — the `glow-haven-api` service needs those files at build time.

## Import checklist

1. GitHub repo: `viviancheruiyot260-sys/Glow-Haven`, branch `main`.
2. **Root directory:** `./`
3. **Framework preset:** **Services** → **Import multi-service project**
4. Deploy, then add environment variables (below).

## Environment variables

Set in Vercel → Project → Settings → Environment Variables:

| Variable | Required | Example / notes |
|----------|----------|-----------------|
| `DATABASE_URI` | **Yes** | `mysql+pymysql://user:pass@host:3306/glow_haven?charset=utf8mb4` |
| `SECRET_KEY` | **Yes** | Random string |
| `JWT_SECRET_KEY` | **Yes** | Random string |
| `MPESA_CALLBACK_URL` | For STK | `https://glow-haven.vercel.app/api/payments/mpesa/callback` |
| `MPESA_CONSUMER_KEY` | For STK | Daraja sandbox/production (never commit) |
| `MPESA_CONSUMER_SECRET` | For STK | Daraja |
| `MPESA_PASSKEY` | For STK | Daraja |
| `VITE_API_URL` | **Leave unset** | Same-origin `/api` routing |

Do **not** use SQLite on Vercel (`USE_SQLITE=1`); the filesystem is ephemeral.

## Verify after deploy

```text
GET https://glow-haven.vercel.app/api/health
```

Expect `"status": "ok"` and `"database_connected": true` once `DATABASE_URI` is valid.

Smoke-test in the browser:

```text
/api/products
/api/auth/login   (POST)
/api/orders
/api/payments/mpesa/stkpush   (POST, when Daraja is configured)
```

## Local development

```bash
cd backend && python app.py          # :5000
cd frontend && npm run dev             # :5173, proxies /api → :5000
```

Optional: `vercel dev` at repo root (Vercel CLI ≥ 48.2.10).

## Validation notes (repo)

- Flask entrypoint: `backend/app.py` exports `app = create_app()`; `entrypoint` is `app:app`.
- Python deps: `backend/requirements.txt` includes root `requirements.txt` for Vercel install in the `backend` service root.
- API function timeout: `maxDuration: 60` on `app.py` (M-Pesa / checkout flows).
- Frontend SPA: service-level rewrites serve `index.html` for client routes; `/assets/*` stays static.

## Alternative: API on Render

See [`render.yaml`](../render.yaml) if you prefer the API off Vercel and `VITE_API_URL` pointing at Render.
