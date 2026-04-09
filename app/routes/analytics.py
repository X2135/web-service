from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db

router = APIRouter()


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    entries = crud.get_habit_records(db=db, skip=0, limit=1000)
    total_entries = len(entries)

    return {
        "total_entries": total_entries,
        "note": "Analytics endpoint placeholder for future metrics.",
    }
