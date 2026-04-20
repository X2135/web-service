from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database import Base, SessionLocal, engine
from app import crud
from scripts.import_data import import_csv_data


def main() -> int:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_name = "initial_habit_seed_v1"

        print("Checking seed status...")

        # Fallback reference from the previous implementation:
        # existing_records = db.query(HabitRecord).count()
        # if existing_records > 0:
        #     print(f"Seed skipped: {existing_records} existing records found.")
        #     return 0

        if crud.check_seed_applied(db, seed_name):
            print("Seed already applied, skipping.")
            return 0

        print("Seed not found, running import...")
        categories, records, skipped = import_csv_data()
        crud.mark_seed_applied(db, seed_name)
        print("Seed applied successfully")
        print(
            "Seed completed: "
            f"categories_created={categories}, records_imported={records}, skipped_rows={skipped}"
        )
        return 0
    except Exception as exc:
        db.rollback()
        print(f"Seed failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
