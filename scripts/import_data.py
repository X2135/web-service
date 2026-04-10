from pathlib import Path
import sys
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database import SessionLocal, engine
from app.models import Base, HabitCategory, HabitRecord

CSV_PATH = PROJECT_ROOT / "data" / "habit_data.csv"


def import_csv_data(csv_path: Path = CSV_PATH) -> tuple[int, int, int]:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)
    column_map = _resolve_column_map(df.columns)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    category_created_count = 0
    record_created_count = 0
    skipped_count = 0

    try:
        category, category_created = _get_or_create_category(
            db,
            name="Fitness",
            description="Workout-related habits",
        )
        if category_created:
            category_created_count += 1

        for index, row in df.iterrows():
            try:
                record = _build_habit_record(row, column_map, category.id)
                if record is None:
                    skipped_count += 1
                    continue
                db.add(record)
                record_created_count += 1
            except Exception as exc:
                skipped_count += 1
                print(f"[WARN] Row {index + 2} skipped: {exc}")

        db.commit()
        return category_created_count, record_created_count, skipped_count
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _build_habit_record(row: pd.Series, column_map: dict[str, str], category_id: int) -> HabitRecord | None:
    record_date_raw = _read_cell(row, column_map["record_date"])
    habit_name = _read_cell(row, column_map["habit_name"])
    completed_raw = _read_cell(row, column_map["completed"])
    duration_raw = _read_cell(row, column_map["duration_minutes"])
    notes_raw = _read_cell(row, column_map["notes"]) if "notes" in column_map else None

    if pd.isna(record_date_raw) or pd.isna(habit_name):
        return None

    duration_minutes: int | None = None
    if not pd.isna(duration_raw):
        duration_minutes = int(float(duration_raw))

    completed = _to_bool(completed_raw, duration_minutes)

    return HabitRecord(
        record_date=pd.to_datetime(record_date_raw).date(),
        habit_name=str(habit_name).strip(),
        category_id=category_id,
        completed=completed,
        duration_minutes=duration_minutes,
        notes=None if pd.isna(notes_raw) else str(notes_raw),
    )


def _resolve_column_map(columns: Any) -> dict[str, str]:
    normalized = {str(col).strip().lower(): str(col) for col in columns}

    def pick(required_key: str, candidates: list[str], optional: bool = False) -> str:
        for candidate in candidates:
            key = candidate.strip().lower()
            if key in normalized:
                return normalized[key]
        if optional:
            return ""
        raise ValueError(f"Missing required CSV column for '{required_key}'. Candidates: {candidates}")

    column_map = {
        "record_date": pick("record_date", ["record_date", "date"]),
        "habit_name": pick("habit_name", ["habit_name", "habit", "habit title"], optional=True),
        "completed": pick("completed", ["completed", "journaling (y/n)", "done"], optional=True),
        "duration_minutes": pick(
            "duration_minutes",
            ["duration_minutes", "workout_duration_min", "duration", "minutes"],
            optional=True,
        ),
        "notes": pick("notes", ["notes", "note", "comment"], optional=True),
    }

    if not column_map["habit_name"]:
        column_map["habit_name"] = "__default_habit_name__"
    if not column_map["completed"]:
        column_map["completed"] = "__derive_completed__"
    if not column_map["duration_minutes"]:
        column_map["duration_minutes"] = "__no_duration__"
    if not column_map["notes"]:
        column_map.pop("notes")

    return column_map


def _read_cell(row: pd.Series, source_col: str) -> Any:
    if source_col == "__default_habit_name__":
        return "Workout"
    if source_col == "__derive_completed__":
        return None
    if source_col == "__no_duration__":
        return None
    return row[source_col]


def _to_bool(value: Any, duration_minutes: int | None) -> bool:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return (duration_minutes or 0) > 0

    text = str(value).strip().lower()
    if text in {"y", "yes", "true", "1", "completed"}:
        return True
    if text in {"n", "no", "false", "0", "not completed"}:
        return False

    return (duration_minutes or 0) > 0


def _get_or_create_category(
    db: Session,
    name: str,
    description: str | None = None,
) -> tuple[HabitCategory, bool]:
    category = db.query(HabitCategory).filter(HabitCategory.name == name).first()
    if category:
        return category, False

    category = HabitCategory(name=name, description=description)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category, True


if __name__ == "__main__":
    categories, records, skipped = import_csv_data()
    print(f"Imported categories: {categories}")
    print(f"Imported records: {records}")
    print(f"Skipped rows: {skipped}")
