"""Quick local API smoke checks using FastAPI TestClient."""

import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.main import app


client = TestClient(app)


def pretty(label: str, status_code: int, payload: dict | list | str) -> None:
    # Standardized console output for easier result comparison.
    print(f"{label}: {status_code} | {json.dumps(payload, ensure_ascii=False)}")


r = client.post("/auth/login", json={"username": "demo", "password": "demo123"})
pretty("login_success", r.status_code, r.json())
token = r.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

r = client.post("/auth/login", json={"username": "demo", "password": "wrong"})
pretty("login_fail", r.status_code, r.json())

r = client.post("/habits/categories", json={"name": "NoTokenCat", "description": "x"})
pretty("protected_no_token", r.status_code, r.json())

r = client.post("/habits/categories", json={"name": "Fitness", "description": "dup"}, headers=headers)
pretty("duplicate_category", r.status_code, r.json())

r = client.post(
    "/habits/records",
    json={
        "record_date": "2024-06-02",
        "habit_name": "Invalid Category",
        "category_id": 9999,
        "completed": True,
        "duration_minutes": 15,
        "notes": "invalid fk test",
    },
    headers=headers,
)
pretty("invalid_category_id", r.status_code, r.json())

r = client.post("/habits/categories", json={"name": "AuthTest2", "description": "for tests"}, headers=headers)
if r.status_code == 200:
    pretty("create_category_ok", r.status_code, r.json())
    cat_id = r.json().get("id")
else:
    pretty("create_category_existing", r.status_code, r.json())
    fetch = client.get("/habits/categories")
    cat_id = next((item["id"] for item in fetch.json() if item["name"] == "AuthTest2"), None)

if cat_id:
    r = client.post(
        "/habits/records",
        json={
            "record_date": "2024-06-03",
            "habit_name": "Auth Protected Record",
            "category_id": cat_id,
            "completed": True,
            "duration_minutes": 25,
            "notes": "created with token",
        },
        headers=headers,
    )
    pretty("create_record_ok", r.status_code, r.json())
    if r.status_code == 200:
        rec_id = r.json().get("id")
        r2 = client.get(f"/habits/records/{rec_id}")
        pretty("get_record_ok", r2.status_code, r2.json())

r = client.get("/habits/categories/99999")
pretty("category_404", r.status_code, r.json())

r = client.get("/habits/records/99999")
pretty("record_404", r.status_code, r.json())
