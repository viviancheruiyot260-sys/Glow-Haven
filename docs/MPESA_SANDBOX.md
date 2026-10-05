# M-Pesa Daraja — Sandbox setup (Glow Haven)

## 1. Safaricom Developer Portal

1. Go to [https://developer.safaricom.co.ke](https://developer.safaricom.co.ke) and sign in.
2. Create an app (e.g. **Glow Haven Sandbox**).
3. Enable **Lipa na M-Pesa Online (STK Push)** for the sandbox app.
4. Copy from the app credentials:
   - **Consumer Key**
   - **Consumer Secret**
5. Under **Test credentials** / STK Push, copy the **Passkey** (online passkey for sandbox).

Official sandbox paybill shortcode: **174379** (used automatically when `MPESA_SHORTCODE` is empty and `MPESA_ENV=sandbox`).

## 2. Callback URL (required for STK)

Daraja must POST payment results to a **public HTTPS URL**. Localhost is not reachable from Safaricom.

**Option A — ngrok (recommended for dev)**

```bash
ngrok http 5000
```

Use the HTTPS URL:

```text
https://YOUR-SUBDOMAIN.ngrok-free.app/api/payments/mpesa/callback
```

**Option B — polling only**

If callback is not set up, Glow Haven still **polls STK status** from the checkout page via `/api/payments/mpesa/query/<order_id>`. A valid callback URL is still required in `.env` for Daraja to accept STK push in many setups—use ngrok when possible.

## 3. `.env` (project root `Glow-Haven/.env`)

```env
MPESA_ENV=sandbox
MPESA_CONSUMER_KEY=your_sandbox_consumer_key
MPESA_CONSUMER_SECRET=your_sandbox_consumer_secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=your_sandbox_passkey
MPESA_CALLBACK_URL=https://YOUR-SUBDOMAIN.ngrok-free.app/api/payments/mpesa/callback
```

Do not commit `.env`. Never commit real production keys.

## 4. Sandbox test phone

Safaricom documents test MSISDN **254708374149** for sandbox STK. Use any format the app accepts (`07…` or `2547…`).

## 5. Run and test

```bash
# Terminal 1 — API (+ built React on :5000)
cd backend
python app.py

# If using ngrok
ngrok http 5000
```

1. Log in, add items to cart, go to **Checkout**.
2. UI should show **Daraja sandbox** (not mock mode).
3. Enter phone → **Pay with M-Pesa** → STK prompt (sandbox).
4. Complete PIN on phone; checkout page polls until **paid**, then redirects to **Orders**.

## 6. Verify configuration

```bash
curl http://127.0.0.1:5000/api/payments/mpesa/config
```

Expect `"configured": true` when all required variables are set.

## 7. Mock mode

If `MPESA_CONSUMER_KEY` or `MPESA_PASSKEY` or `MPESA_CALLBACK_URL` is missing, checkout uses **mock payment** (no STK) so you can develop without Daraja.
