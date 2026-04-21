# Habit & Productivity Analytics API

A coursework Web Services API project built with FastAPI. The service provides CRUD operations for habit categories and habit records, an analytics summary endpoint, and JWT-based authentication for protected write operations.

## 1) Project Overview

This API supports habit tracking and productivity analysis with the following core capabilities:

- CRUD for `habit_categories` and `habit_records`
- Analytics endpoint: `GET /analytics/summary`
- JWT authentication for protected endpoints
- Structured validation and unified error response shape

## 2) Setup Instructions

Run the following from your terminal step-by-step:

### Step 1 — Clone repository

```bash
git clone <your-repo-url>
cd <repo-folder>
```

### Step 2 — Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — (Recommended) import local CSV seed data

```bash
python scripts/import_data.py
```

### Step 5 — Run API server

```bash
python -m uvicorn app.main:app --reload
```

## 3) Run Instructions

- API base URL: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## 3.1) Frontend Usage (for Demo and Presentation)

This project also includes a lightweight frontend dashboard in `frontend/` for coursework demonstration. It is used to quickly show API health, login status, analytics cards, and demo CRUD actions.

### Start frontend locally

Open a new terminal from project root and run:

```bash
python3 -m http.server 5500
```

Open in browser:

- `http://127.0.0.1:5500/frontend/?local=1` (connect to local FastAPI)
- `http://127.0.0.1:5500/frontend/` (connect to deployed backend by default)
- Deployed frontend URL: `https://web-service-2-8jgm.onrender.com/`

### Frontend Layout Guide (What each area does)

When you open the frontend page, the interface is divided into these functional blocks:

1. **Header (top area)**
  - **Service Status**: shows whether backend is reachable (`Online` / `Offline`).
  - **Authentication**: shows login state (`Authenticated` / `Not authenticated`).
  - **API Base URL**: shows which backend URL the page is currently calling.

2. **Global Message Bar**
  - Displays success/failure feedback after each action (for example login success, create failed, etc.).

3. **Summary Cards**
  - **Total Records**: total habit records in database.
  - **Completed Records**: number of records with `completed=true`.
  - **Completion Rate**: completion percentage from backend analytics.
  - **Average Duration**: average `duration_minutes` from backend analytics.

4. **Controlled Demo Actions Panel**
  - Contains operation buttons for auth + CRUD demo flow.
  - Intended for step-by-step live demonstration in presentation.

5. **Analytics Evidence Panel**
  - **Records by Category**: top category counts from `/analytics/summary`.
  - **Daily Completion Trend**: recent daily `completed/total` trend rows.

### Frontend Button Guide (What each click does)

1. **Sign in (Demo Account)**
  - Calls `POST /auth/login` with demo credentials.
  - Saves JWT token in browser localStorage.
  - Enables protected write operations.

2. **Create Category**
  - Calls `POST /habits/categories` with name `Demo Category`.
  - Stores created id in frontend state and refreshes analytics.

3. **Create Record**
  - Calls `POST /habits/records` with habit name `Demo Habit`.
  - Inserts one new record and refreshes analytics.

4. **Delete Demo Category**
  - Calls `DELETE /habits/categories/{id}` for latest `Demo Category`.
  - If related records exist, delete demo record first.

5. **Delete Demo Record**
  - Calls `DELETE /habits/records/{id}` for latest `Demo Habit` record.
  - Refreshes analytics after deletion.

6. **Refresh Analytics**
  - Calls `GET /analytics/summary` only.
  - Re-renders all summary cards and insight lists.

### Frontend quick workflow (recommended demo order)

1. Click **Sign in (Demo Account)**.
2. Click **Create Category**.
3. Click **Create Record**.
4. Click **Refresh Analytics** and observe card/list updates.
5. Click **Delete Demo Record**.
6. Click **Delete Demo Category**.

Expected result: each action returns a success message in the message bar and keeps Service Status as `Online`.

## 4) API Documentation

- Local file: `docs/API_Documentation.pdf`
- Repository link: `https://github.com/X2135/web-service/blob/main/docs/API_Documentation.pdf`


## 5) Deployment Information

- Current deployed API URL: `https://web-service-1-iox1.onrender.com`
- Swagger UI: `https://web-service-1-iox1.onrender.com/docs`
- ReDoc: `https://web-service-1-iox1.onrender.com/redoc`

### 5.1) Render Configuration (Used in This Project)

- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Required environment variables:
  - `APP_ENV=production`
  - `DATABASE_URL=<Render Internal Database URL>`
  - `SECRET_KEY=<long-random-string>`
  - `ALGORITHM=HS256`
  - `ACCESS_TOKEN_EXPIRE_MINUTES=60`

### 5.2) Seed Behavior on Render (Important)

This project does **not** auto-seed during app startup. Initial import is handled by `scripts/predeploy_seed_once.py`.

- If your Render plan supports Pre-Deploy Command, run:
  - `python scripts/predeploy_seed_once.py`
- If Pre-Deploy is unavailable on free plan, run seed once from local terminal using Render **External Database URL**:

```bash
cd "/Users/lcx/Desktop/web service"
export APP_ENV=production
export DATABASE_URL='<Render External Database URL>'
python scripts/predeploy_seed_once.py
unset DATABASE_URL APP_ENV
```

The script is idempotent via `seed_history` and avoids duplicate imports.

## 6) Authentication Summary

JWT is used for authentication. Obtain a token via `POST /auth/login` (or `POST /auth/token` for Swagger OAuth2 form), then send:

```http
Authorization: Bearer <access_token>
```

Protected endpoints:

- `GET /auth/me`
- `POST /habits/categories`
- `PUT /habits/categories/{category_id}`
- `DELETE /habits/categories/{category_id}`
- `POST /habits/records`
- `PUT /habits/records/{record_id}`
- `DELETE /habits/records/{record_id}`

Read endpoints remain open for coursework demonstration (e.g., listing categories/records and analytics summary).

## 7) Example Usage (Login + Protected Call)

```bash
# 1) Login and copy access_token from response
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}'

# 2) Call a protected endpoint with copied token
curl -X POST "http://127.0.0.1:8000/habits/categories" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <PASTE_ACCESS_TOKEN_HERE>" \
  -d '{"name":"Learning","description":"Reading and study habits"}'
```

## 8) Project Structure

```text
.
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── auth.py
│   └── routes/
│       ├── auth.py
│       ├── habits.py
│       └── analytics.py
├── data/
├── scripts/
├── tests/
├── docs/
└── frontend/
```

## 9) Testing

- Run tests:

```bash
pytest
```

- Current test scope covers auth, CRUD, validation, error handling, and analytics.
- Latest project result: **22 tests passed**.

## 9.1) Command-Line Testing for All Core Functions

If you want to test all key features without frontend, use the CLI flow below.

### A) Verify local DB state (table existence + counts)

```bash
python scripts/verify_db.py
```

What it does:
- Checks local database connectivity and table/data status.
- Quickly confirms whether your local environment is ready for API run/tests.

### B) Run API behavior check script (auth + protected + error paths)

```bash
python scripts/run_api_checks.py
```

This script checks login success/failure, missing token behavior, duplicate category handling, invalid category reference, create/read flows, and not-found responses.

### C) Run full automated test suite

```bash
pytest -q
```

What it does:
- Runs all automated API tests under `tests/`.
- Verifies auth, CRUD behavior, validation boundaries, error handling, and analytics contract.

### D) Manual endpoint checks with curl (recommended for report evidence)

Run API locally first (`python -m uvicorn app.main:app --reload`), then execute:

```bash
# 1) health
curl -s "http://127.0.0.1:8000/"

# 2) login
curl -s -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}'

# 3) list categories (public)
curl -s "http://127.0.0.1:8000/habits/categories?limit=5"

# 4) analytics (public)
curl -s "http://127.0.0.1:8000/analytics/summary"
```

What each command validates:
- **health**: service process is running and reachable.
- **login**: credential flow and JWT issuance are working.
- **list categories**: public read endpoint returns JSON list.
- **analytics**: aggregation endpoint responds correctly.

### E) Manual protected CRUD test (token + write operations)

```bash
# 1) login and capture token
TOKEN=$(curl -s -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}' | python -c 'import sys, json; print(json.load(sys.stdin)["access_token"])')

# 2) create category (protected)
curl -s -X POST "http://127.0.0.1:8000/habits/categories" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"CLI Demo Category","description":"created from CLI"}'

# 3) create record (protected)
curl -s -X POST "http://127.0.0.1:8000/habits/records" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"record_date":"2024-06-10","habit_name":"CLI Demo Habit","category_id":1,"completed":true,"duration_minutes":25,"notes":"cli test"}'
```

What this block validates:
- Bearer token can be parsed and reused.
- Protected write endpoints enforce auth and accept valid payloads.
- New writes affect persisted data.

### F) Deployed endpoint quick checks (backend)

```bash
BASE="https://web-service-1-iox1.onrender.com"

curl -s "$BASE/"
curl -s "$BASE/habits/categories?skip=0&limit=50"
curl -s "$BASE/analytics/summary"
```

What it does:
- Confirms deployed backend health, public reads, and analytics output.

### G) Deployed frontend checks

Frontend URL:

```text
https://web-service-2-8jgm.onrender.com/
```

Checklist:
- Page loads without 404/blank screen.
- Header status shows backend reachable.
- Demo login succeeds and auth status turns to `Authenticated`.
- Create/refresh/delete actions return success messages and update analytics cards/lists.

## 9.2) How to Use This Project (Recommended Order)

1. Setup environment and start API.
2. Open Swagger (`/docs`) and verify routes quickly.
3. Choose one interaction mode:
   - frontend demo (`frontend/`) for presentation;
   - CLI (`curl` + scripts + pytest) for reproducible validation.
4. Use JWT token for protected write operations (POST/PUT/DELETE).
5. Use analytics endpoint to summarize habit completion and trends.

## 10) Database

- Local development/testing: SQLite (`habits.db`)
- Production deployment: PostgreSQL via `DATABASE_URL`
- Production safeguard: when environment is production, missing `DATABASE_URL` raises an error (no SQLite fallback)

## 11) Seed Logic (No Duplicate Import)

To avoid duplicate imports on redeploy, this project uses a seed tracking mechanism:

- Seed marker stored in `seed_history`
- Script `scripts/predeploy_seed_once.py` checks whether the named seed has already been applied
- If already applied, seed import is skipped
- If not applied, import runs and then records the seed marker

## 12) Screenshots

### Swagger UI (`/docs`)

![Swagger UI Screenshot](docs/images/swagger-ui.png)

### Analytics Endpoint Response (`/analytics/summary`)

![Analytics Summary Screenshot](docs/images/analytics-summary.png)

### GenAI Conversation Evidence

![ChatGPT conversation on API CRUD route design](docs/images/image%20for%20chatgpt.png)

![ChatGPT conversation on reseeding and persistence strategy](docs/images/image%20for%20chatgpt2.png)

---

## Coursework Notes

- This repository is prepared for university Web Services API submission.
- API documentation and technical report are maintained under `docs/`.
- The implementation, validation, and final decisions remain human-led, with GenAI used as an assistive tool.
