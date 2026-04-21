"""CSV import utility that maps raw habit data into normalized DB records."""

from pathlib import Path
import sys
from collections import Counter
from datetime import date
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database import SessionLocal, engine
from app.models import Base, HabitCategory, HabitRecord

CSV_PATH = PROJECT_ROOT / "data" / "habit_data.csv"

# Category design for coursework:
# - Fitness: activity-driven rows (workout minutes > 0)
# - Wellness: low-intensity wellbeing rows (journaling/reading patterns)
# - Health: remaining baseline lifestyle rows
CATEGORY_DEFINITIONS: dict[str, str] = {
    "Fitness": "Physical activity and workout-focused habits",
    "Wellness": "Mindfulness and reflective wellbeing habits",
    "Health": "General health maintenance and recovery patterns",
}


def import_csv_data(csv_path: Path = CSV_PATH) -> tuple[int, int, int]:
    # Imports categories and records idempotently where possible.
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)
    column_map = _resolve_column_map(df.columns)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    category_created_count = 0
    record_created_count = 0
    skipped_count = 0
    category_distribution: Counter[str] = Counter()
    imported_durations: list[int] = []

    try:
        categories, category_created_count = _ensure_categories(db)
        existing_keys = _load_existing_record_keys(db)

        for index, row in df.iterrows():
            try:
                record = _build_habit_record(row, column_map, categories)
                if record is None:
                    skipped_count += 1
                    continue

                record_key = (record.record_date, record.habit_name, record.category_id)
                if record_key in existing_keys:
                    skipped_count += 1
                    continue

                db.add(record)
                existing_keys.add(record_key)
                record_created_count += 1

                category_name = _category_name_by_id(categories, record.category_id)
                category_distribution[category_name] += 1
                if record.duration_minutes is not None:
                    imported_durations.append(record.duration_minutes)
            except Exception as exc:
                skipped_count += 1
                print(f"[WARN] Row {index + 2} skipped: {exc}")

        db.commit()
        _print_import_summary(
            imported_count=record_created_count,
            skipped_count=skipped_count,
            category_distribution=category_distribution,
            durations=imported_durations,
        )
        return category_created_count, record_created_count, skipped_count
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _build_habit_record(
    row: pd.Series,
    column_map: dict[str, str],
    categories: dict[str, HabitCategory],
) -> HabitRecord | None:
    record_date_raw = _read_cell(row, column_map["record_date"])
    workout_raw = _read_cell(row, column_map["duration_minutes"])
    sleep_raw = _read_cell(row, column_map["sleep_hours"])
    journaling_raw = _read_cell(row, column_map["journaling"])
    reading_raw = _read_cell(row, column_map["reading_min"])
    notes_raw = _read_cell(row, column_map["notes"])

    parsed_date = _parse_date(record_date_raw)
    if parsed_date is None:
        return None

    duration_minutes = _to_int_or_none(workout_raw)
    if duration_minutes is None:
        duration_minutes = 0
    if duration_minutes < 0:
        raise ValueError("duration_minutes cannot be negative")

    sleep_hours = _to_float_or_none(sleep_raw)
    journaling = _to_yes_no_bool(journaling_raw)
    reading_minutes = _to_int_or_none(reading_raw) or 0

    category_name = _derive_category_name(
        duration_minutes=duration_minutes,
        journaling=journaling,
        reading_minutes=reading_minutes,
    )
    category = categories[category_name]

    habit_name = _derive_habit_name(
        duration_minutes=duration_minutes,
        journaling=journaling,
        reading_minutes=reading_minutes,
        sleep_hours=sleep_hours,
    )

    # Completion is inferred from multiple signals, not only workout duration.
    # A day is treated as completed if any of the following is true:
    # 1) workout duration reaches the effective threshold (>= 20 minutes)
    # 2) journaling activity is present
    # 3) reading reaches the threshold (>= 20 minutes)
    # 4) sleep reaches a basic wellness threshold (>= 7 hours)
    # This rule keeps behavior explainable while matching the dataset characteristics.
    completed = bool(
        duration_minutes >= 20
        or journaling
        or reading_minutes >= 20
        or (sleep_hours is not None and sleep_hours >= 7)
    )

    notes = _build_notes(notes_raw)

    return HabitRecord(
        record_date=parsed_date,
        habit_name=habit_name,
        category_id=category.id,
        completed=completed,
        duration_minutes=duration_minutes,
        notes=notes,
    )


def _resolve_column_map(columns: Any) -> dict[str, str]:
    # Resolve flexible CSV headers to canonical internal keys.
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
        "duration_minutes": pick(
            "duration_minutes",
            ["duration_minutes", "workout_duration_min", "duration", "minutes"],
            optional=True,
        ),
        "sleep_hours": pick("sleep_hours", ["sleep_hours", "sleep"], optional=True),
        "journaling": pick("journaling", ["journaling (y/n)", "journaling", "journaled"], optional=True),
        "reading_min": pick("reading_min", ["reading_min", "reading", "reading_minutes"], optional=True),
        "notes": pick("notes", ["notes", "note", "comment"], optional=True),
    }

    if not column_map["duration_minutes"]:
        column_map["duration_minutes"] = "__no_duration__"
    if not column_map["sleep_hours"]:
        column_map["sleep_hours"] = "__no_sleep__"
    if not column_map["journaling"]:
        column_map["journaling"] = "__no_journaling__"
    if not column_map["reading_min"]:
        column_map["reading_min"] = "__no_reading__"
    if not column_map["notes"]:
        column_map["notes"] = "__default_notes__"

    return column_map


def _read_cell(row: pd.Series, source_col: str) -> Any:
    if source_col in {"__no_duration__", "__no_sleep__", "__no_journaling__", "__no_reading__"}:
        return None
    if source_col == "__default_notes__":
        return None
    return row[source_col]


def _parse_date(value: Any) -> date | None:
    if value is None or pd.isna(value):
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date()


def _to_int_or_none(value: Any) -> int | None:
    if value is None or pd.isna(value):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _to_float_or_none(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_yes_no_bool(value: Any) -> bool:
    if value is None or pd.isna(value):
        return False
    text = str(value).strip().lower()
    return text in {"y", "yes", "true", "1"}


def _derive_category_name(duration_minutes: int, journaling: bool, reading_minutes: int) -> str:
    # Category logic is intentionally explicit for report explainability.
    # Priority 1: if there is workout activity, classify as Fitness.
    if duration_minutes > 0:
        return "Fitness"

    # Priority 2: if no workout but mindfulness/reading signals exist, classify as Wellness.
    if journaling or reading_minutes >= 20:
        return "Wellness"

    # Otherwise, classify as general Health maintenance.
    return "Health"


def _derive_habit_name(
    duration_minutes: int,
    journaling: bool,
    reading_minutes: int,
    sleep_hours: float | None,
) -> str:
    # Habit naming strategy:
    # Provide multiple interpretable activity types instead of a single fixed label.
    if duration_minutes >= 45:
        return "Workout - Intense Session"
    if duration_minutes > 0:
        return "Workout - Light Session"
    if journaling and reading_minutes >= 20:
        return "Mindfulness & Reading"
    if sleep_hours is not None and sleep_hours < 6:
        return "Sleep Recovery Focus"
    return "Daily Wellness Check-in"


def _build_notes(notes_raw: Any) -> str:
    base_note = "Imported from Kaggle dataset (90-day habit tracker)."
    if notes_raw is None or pd.isna(notes_raw):
        return base_note
    return f"{base_note} Source note: {str(notes_raw).strip()}"


def _ensure_categories(db: Session) -> tuple[dict[str, HabitCategory], int]:
    created_count = 0
    categories: dict[str, HabitCategory] = {}

    for name, description in CATEGORY_DEFINITIONS.items():
        category = db.query(HabitCategory).filter(HabitCategory.name == name).first()
        if not category:
            category = HabitCategory(name=name, description=description)
            db.add(category)
            db.flush()
            created_count += 1
        categories[name] = category

    return categories, created_count


def _load_existing_record_keys(db: Session) -> set[tuple[date, str, int]]:
    existing_records = db.query(HabitRecord.record_date, HabitRecord.habit_name, HabitRecord.category_id).all()
    return {(item.record_date, item.habit_name, item.category_id) for item in existing_records}


def _category_name_by_id(categories: dict[str, HabitCategory], category_id: int) -> str:
    for name, category in categories.items():
        if category.id == category_id:
            return name
    return "Unknown"


def _print_import_summary(
    imported_count: int,
    skipped_count: int,
    category_distribution: Counter[str],
    durations: list[int],
) -> None:
    # Prints compact import evidence used in deployment logs/reporting.
    average_duration = (sum(durations) / len(durations)) if durations else 0

    print("Import Summary:")
    print(f"- Total records imported: {imported_count}")
    print(f"- Skipped rows: {skipped_count}")
    print("- Categories distribution:")
    if category_distribution:
        for category_name, count in sorted(category_distribution.items()):
            print(f"  - {category_name}: {count}")
    else:
        print("  - No records imported.")
    print(f"- Average duration_minutes: {average_duration:.2f}")


if __name__ == "__main__":
    categories, records, skipped = import_csv_data()
    print(f"Imported categories: {categories}")
    print(f"Imported records: {records}")
    print(f"Skipped rows: {skipped}")
