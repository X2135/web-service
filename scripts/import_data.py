from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models import Base, HabitCategory, HabitRecord

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = PROJECT_ROOT / "data" / "habit_data.csv"


def import_csv_data(csv_path: Path = CSV_PATH) -> int:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    created_count = 0

    try:
        category = _get_or_create_category(db, name="Fitness", description="Workout-related habits")

        for _, row in df.iterrows():
            workout_minutes = int(row["Workout_Duration_Min"])
            record = HabitRecord(
                record_date=pd.to_datetime(row["Date"]).date(),
                habit_name="Workout",
                category_id=category.id,
                completed=workout_minutes > 0,
                duration_minutes=workout_minutes,
                notes=None,
            )
            db.add(record)
            created_count += 1

        db.commit()
        return created_count
    finally:
        db.close()


def _get_or_create_category(db: Session, name: str, description: str | None = None) -> HabitCategory:
    category = db.query(HabitCategory).filter(HabitCategory.name == name).first()
    if category:
        return category

    category = HabitCategory(name=name, description=description)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


if __name__ == "__main__":
    count = import_csv_data()
    print(f"Imported {count} records into SQLite.")
