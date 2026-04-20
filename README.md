# Habit & Productivity Analytics API

A data-driven REST API coursework project built with FastAPI, SQLite, and SQLAlchemy, using a Kaggle 90-day habit tracker dataset as the core data source.  
The project includes secure CRUD operations, JWT authentication, analytics endpoints, automated tests, and a frontend dashboard that consumes real backend API responses.

---

## Project Overview

This project demonstrates an end-to-end backend workflow for habit and productivity tracking:

- Build a structured REST API with clear resource models
- Import and normalize CSV dataset records into a relational database
- Protect write operations with JWT-based authentication
- Provide analytics through a dedicated summary endpoint
- Present results in a browser-based dashboard

The goal is to deliver a professional, explainable, and demo-ready coursework submission.

---

## Key Features

- Full CRUD for:
  - Habit categories
  - Habit records
- JWT authentication for protected endpoints
- CSV-to-SQLite data import pipeline
- Analytics summary endpoint: `/analytics/summary`
- Consistent error handling and HTTP status codes
- Pytest-based API test suite
- Frontend dashboard (HTML/CSS/JavaScript) connected to real API data

---

## Tech Stack

- FastAPI
- SQLite
- SQLAlchemy
- Pydantic
- Pandas
- Pytest
- HTML / CSS / JavaScript

---

## Dataset

- Source: Kaggle 90-day habit tracker dataset
- Input files:
  - `data/habit_data.csv`
  - `90_day_habit_tracker.csv` (raw reference file)
- Import script: `scripts/import_data.py`

### Mapping Summary

The import pipeline:

- Reads CSV with Pandas
- Resolves and validates source columns
- Parses date and activity-related fields
- Maps records into:
  - `habit_categories`
  - `habit_records`
- Derives category, habit label, and completion status with explicit rule-based logic
- Handles duplicate/invalid rows and prints import summary statistics

---

## Project Structure

```text
.
├── app/
│   ├── main.py                # FastAPI app entrypoint, router registration, exception handling
│   ├── database.py            # SQLite engine and DB session management
│   ├── models.py              # SQLAlchemy ORM models
│   ├── schemas.py             # Pydantic request/response schemas
│   ├── crud.py                # Database CRUD logic + analytics aggregation
│   ├── auth.py                # JWT utilities and auth dependency
│   └── routes/
│       ├── auth.py            # /auth endpoints
│       ├── habits.py          # /habits CRUD endpoints
│       └── analytics.py       # /analytics/summary endpoint
├── data/
│   └── habit_data.csv         # Main dataset used for import
├── frontend/
│   ├── index.html             # Dashboard UI
│   ├── script.js              # API integration and rendering logic
│   └── style.css              # Dashboard styling
├── scripts/
│   ├── import_data.py         # CSV -> SQLite import pipeline
│   ├── run_api_checks.py      # API behavior check script
│   └── verify_db.py           # Database verification script
├── tests/
│   ├── test_api_crud.py       # API integration tests
│   └── ...                    # Additional test files
├── requirements.txt           # Python dependencies
└── habits.db                  # SQLite database file generated after local data import
```

---

## Setup & Run Instructions

All commands below should be run from the project root directory.

### 1) Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Import dataset into SQLite

```bash
python scripts/import_data.py
```

### 4) Start FastAPI server

```bash
python -m uvicorn app.main:app --reload
```

### 5) Open Swagger UI

- `http://127.0.0.1:8000/docs`

### 6) Start frontend dashboard (new terminal)

From the project root directory, run:

```bash
python -m http.server 5500
```

Then open:

- `http://127.0.0.1:5500/frontend/`

### 7) Run tests

```bash
pytest -q
```

---

## API Overview

### Authentication

- `POST /auth/login`
- `GET /auth/me`

### Habit Categories

- `GET /habits/categories`
- `GET /habits/categories/{category_id}`
- `POST /habits/categories`
- `PUT /habits/categories/{category_id}`
- `DELETE /habits/categories/{category_id}`

### Habit Records

- `GET /habits/records`
- `GET /habits/records/{record_id}`
- `POST /habits/records`
- `PUT /habits/records/{record_id}`
- `DELETE /habits/records/{record_id}`

### Analytics

- `GET /analytics/summary`

---

## Authentication & Error Handling

- JWT login is provided through `POST /auth/login`
- Protected endpoints require `Authorization: Bearer <token>`
- Protected write operations include create/update/delete for categories and records
- API returns consistent status-based error responses, including:
  - `400` bad request/business rule violations
  - `401` unauthorized/invalid credentials/token
  - `404` resource not found
- Error payloads follow a consistent structure to simplify frontend handling and debugging

---

## Testing

Pytest tests cover key API behavior, including:

- Authentication success and failure
- Access control for protected endpoints
- CRUD flows for categories and records
- Duplicate category and invalid foreign-key scenarios
- Not-found behavior (404)
- Analytics summary endpoint response checks
- Boundary validation scenarios (invalid payload values)
- Unified error response format checks

Run tests with:

```bash
pytest -q
```

---

## API Documentation

- Interactive docs (Swagger UI): `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Final API documentation PDF for coursework submission: `docs/API_Documentation.pdf`

---

## Deployment / Running Environment

- Current setup targets local execution for coursework demonstration.
- Backend runs on FastAPI + Uvicorn; frontend is served as static files via `python -m http.server`.
- Default local addresses:
  - Backend: `http://127.0.0.1:8000`
  - Frontend: `http://127.0.0.1:5500/frontend/`

---

## Coursework Submission Components

- **Public repository**: this GitHub project (source code, scripts, tests, frontend)
- **API documentation**: `docs/API_Documentation.pdf`
- **Technical report**: `docs/Technical_Report.pdf`
- **Presentation slides**: `docs/Presentation_Slides.pdf`

---

## Notes / Limitations

- Authentication is demo-level and intended for coursework demonstration
- Analytics is intentionally concise (summary-level metrics, not advanced forecasting)
- Dataset mapping uses explainable rule-based transformations
- SQLite is used for local development and demonstration rather than production-scale deployment

---

## Coursework Value

This repository is designed to support both GitHub submission and oral presentation by emphasizing:

- Clear architecture
- Explainable data handling
- Verifiable API behavior
- Practical frontend-backend integration
