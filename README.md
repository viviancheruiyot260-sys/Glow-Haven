# Glow Haven 💄✨

> Your beauty. Your glow.

Glow Haven is a modern, responsive beauty e-commerce website where customers can browse and purchase skincare, makeup, haircare, fragrances, and beauty accessories.

## Features

- Browse and search products
- Filter and sort products
- Shopping cart
- M-Pesa checkout (Daraja STK push + local mock mode when credentials are not set)
- Order management
- Responsive design
- JWT authentication

## Project flow

**Browse → Product → Cart → Checkout → M-Pesa → Order confirmation**

## Setup

### 1. MySQL database

Create the database and tables:

```bash
mysql -u root -p < backend/database.sql
```

### 2. Environment

Copy `.env.example` to `.env` and set your MySQL password (and other values as needed):

```env
USE_SQLITE=0
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=glow_haven
MYSQL_USER=root
MYSQL_PASSWORD=YOUR_MYSQL_PASSWORD
```

Optional: set `USE_SQLITE=1` only if you want a local SQLite file instead of MySQL.

**M-Pesa Daraja (sandbox):** See [docs/MPESA_SANDBOX.md](docs/MPESA_SANDBOX.md). Leave Daraja keys empty for mock checkout during local dev.

### 3. Python dependencies

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r ../requirements.txt
```

### 4. Verify database connection

```bash
python check_db.py
```

### 5. Frontend (React + Vite)

```bash
cd ../frontend
npm install
npm run build
```

**Development UI** (with Flask API on port 5000):

```bash
npm run dev
```

→ [http://127.0.0.1:5173](http://127.0.0.1:5173) (proxies `/api` to Flask)

### 6. Run backend

```bash
cd ../backend
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) after building the frontend.

## Project structure

```text
glow-haven/
├── frontend/          # React (Vite) — build output in frontend/dist
├── backend/           # Flask API, models, M-Pesa service
│   ├── database.sql   # MySQL schema
│   └── check_db.py    # Connection test utility
├── assets/
├── requirements.txt
└── README.md
```
