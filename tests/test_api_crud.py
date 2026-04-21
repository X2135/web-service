"""End-to-end API tests for auth, CRUD, analytics, and error contracts."""

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

TEST_DB_PATH = Path("test_habits.db")
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    # Route all DB dependencies to an isolated SQLite test database.
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function() -> None:
    # Reset schema before each test to keep cases independent.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_module() -> None:
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


def login_and_get_token() -> str:
    # Helper for protected endpoint tests.
    response = client.post("/auth/login", json={"username": "demo", "password": "demo123"})
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_headers() -> dict:
    token = login_and_get_token()
    return {"Authorization": f"Bearer {token}"}


def create_category(name: str = "Learning", description: str = "Reading habits") -> dict:
    response = client.post(
        "/habits/categories",
        json={"name": name, "description": description},
        headers=auth_headers(),
    )
    assert response.status_code == 201
    return response.json()


def create_record(category_id: int) -> dict:
    # Creates a canonical record used by multiple tests.
    response = client.post(
        "/habits/records",
        json={
            "record_date": "2024-06-01",
            "habit_name": "Reading",
            "category_id": category_id,
            "completed": True,
            "duration_minutes": 30,
            "notes": "test",
        },
        headers=auth_headers(),
    )
    assert response.status_code == 201
    return response.json()


def test_login_success_returns_token() -> None:
    response = client.post("/auth/login", json={"username": "demo", "password": "demo123"})

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_failure_returns_401() -> None:
    response = client.post("/auth/login", json={"username": "demo", "password": "wrong"})

    assert response.status_code == 401


def test_protected_endpoint_without_token_returns_401() -> None:
    response = client.post("/habits/categories", json={"name": "NoToken", "description": "x"})

    assert response.status_code == 401


def test_create_category_success() -> None:
    response = client.post(
        "/habits/categories",
        json={"name": "Learning", "description": "Reading habits"},
        headers=auth_headers(),
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Learning"


def test_create_duplicate_category_returns_400() -> None:
    create_category(name="Learning")

    response = client.post(
        "/habits/categories",
        json={"name": "Learning", "description": "Duplicate"},
        headers=auth_headers(),
    )

    assert response.status_code == 400


def test_get_existing_category_returns_200() -> None:
    category = create_category(name="Fitness")

    response = client.get(f"/habits/categories/{category['id']}")

    assert response.status_code == 200
    assert response.json()["name"] == "Fitness"


def test_get_missing_category_returns_404() -> None:
    response = client.get("/habits/categories/999")

    assert response.status_code == 404


def test_update_category_success() -> None:
    category = create_category(name="Study")

    response = client.put(
        f"/habits/categories/{category['id']}",
        json={"description": "Updated description"},
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert response.json()["description"] == "Updated description"


def test_delete_category_success() -> None:
    category = create_category(name="DeleteMe")

    response = client.delete(f"/habits/categories/{category['id']}", headers=auth_headers())

    assert response.status_code == 204
    assert response.text == ""


def test_delete_missing_category_returns_404() -> None:
    response = client.delete("/habits/categories/999", headers=auth_headers())

    assert response.status_code == 404


def test_create_record_success() -> None:
    category = create_category(name="Reading")

    response = client.post(
        "/habits/records",
        json={
            "record_date": "2024-06-01",
            "habit_name": "Reading",
            "category_id": category["id"],
            "completed": True,
            "duration_minutes": 30,
            "notes": "test",
        },
        headers=auth_headers(),
    )

    assert response.status_code == 201
    assert response.json()["habit_name"] == "Reading"


def test_create_record_with_missing_category_returns_400() -> None:
    response = client.post(
        "/habits/records",
        json={
            "record_date": "2024-06-01",
            "habit_name": "Invalid",
            "category_id": 999,
            "completed": True,
            "duration_minutes": 10,
            "notes": "bad fk",
        },
        headers=auth_headers(),
    )

    assert response.status_code == 400


def test_get_existing_record_returns_200() -> None:
    category = create_category(name="Workout")
    record = create_record(category_id=category["id"])

    response = client.get(f"/habits/records/{record['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == record["id"]


def test_get_missing_record_returns_404() -> None:
    response = client.get("/habits/records/999")

    assert response.status_code == 404


def test_update_record_success() -> None:
    category = create_category(name="Meditation")
    record = create_record(category_id=category["id"])

    response = client.put(
        f"/habits/records/{record['id']}",
        json={"completed": False, "notes": "updated"},
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert response.json()["completed"] is False
    assert response.json()["notes"] == "updated"


def test_delete_record_success() -> None:
    category = create_category(name="DeleteRecord")
    record = create_record(category_id=category["id"])

    response = client.delete(f"/habits/records/{record['id']}", headers=auth_headers())

    assert response.status_code == 204
    assert response.text == ""


def test_delete_missing_record_returns_404() -> None:
    response = client.delete("/habits/records/999", headers=auth_headers())

    assert response.status_code == 404


def test_analytics_summary_returns_expected_metrics() -> None:
    category_a = create_category(name="Fitness")
    category_b = create_category(name="Wellness")

    client.post(
        "/habits/records",
        json={
            "record_date": "2024-06-01",
            "habit_name": "Run",
            "category_id": category_a["id"],
            "completed": True,
            "duration_minutes": 30,
            "notes": "r1",
        },
        headers=auth_headers(),
    )
    client.post(
        "/habits/records",
        json={
            "record_date": "2024-06-01",
            "habit_name": "Read",
            "category_id": category_b["id"],
            "completed": False,
            "duration_minutes": 10,
            "notes": "r2",
        },
        headers=auth_headers(),
    )

    response = client.get("/analytics/summary")
    assert response.status_code == 200

    payload = response.json()
    assert payload["total_records"] == 2
    assert payload["completed_records"] == 1
    assert payload["completion_rate"] == 50.0
    assert payload["average_duration"] == 20.0
    assert "records_per_category" in payload
    assert "daily_trend" in payload
    assert len(payload["daily_trend"]) == 1


def test_boundary_invalid_duration_returns_422() -> None:
    category = create_category(name="BoundaryCat")
    response = client.post(
        "/habits/records",
        json={
            "record_date": "2024-06-01",
            "habit_name": "Bad Duration",
            "category_id": category["id"],
            "completed": True,
            "duration_minutes": -1,
            "notes": "invalid",
        },
        headers=auth_headers(),
    )

    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
    assert body["code"] == "VALIDATION_ERROR"


def test_boundary_empty_category_name_returns_422() -> None:
    response = client.post(
        "/habits/categories",
        json={"name": "", "description": "invalid"},
        headers=auth_headers(),
    )

    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
    assert body["code"] == "VALIDATION_ERROR"


def test_not_found_error_has_unified_shape() -> None:
    response = client.get("/habits/categories/999")
    assert response.status_code == 404
    body = response.json()
    assert body["detail"] == "Category not found."
    assert body["code"] == "CATEGORY_NOT_FOUND"
