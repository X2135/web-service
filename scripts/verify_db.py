"""Inspect local SQLite content for quick post-import verification."""

from pathlib import Path
import sys

from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.models import HabitCategory, HabitRecord

DB_PATH = Path("habits.db")
DATABASE_URL = "sqlite:///./habits.db"


def verify_database(sample_size: int = 5) -> None:
    # Prints table counts and random sample rows for sanity checking.
    print(f"DB file exists: {DB_PATH.exists()} ({DB_PATH.resolve()})")

    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

    with Session(engine) as db:
        category_count = db.query(func.count(HabitCategory.id)).scalar() or 0
        record_count = db.query(func.count(HabitRecord.id)).scalar() or 0

        print(f"habit_categories count: {category_count}")
        print(f"habit_records count: {record_count}")

        samples = (
            db.query(HabitRecord)
            .order_by(func.random())
            .limit(sample_size)
            .all()
        )

        print("Sample habit_records:")
        for item in samples:
            print(
                {
                    "id": item.id,
                    "record_date": str(item.record_date),
                    "habit_name": item.habit_name,
                    "category_id": item.category_id,
                    "completed": item.completed,
                    "duration_minutes": item.duration_minutes,
                    "notes": item.notes,
                }
            )


if __name__ == "__main__":
    verify_database()
