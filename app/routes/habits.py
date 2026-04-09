from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter()


@router.get("/categories", response_model=list[schemas.HabitCategory])
def list_categories(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return crud.get_categories(db=db, skip=skip, limit=limit)


@router.post("/categories", response_model=schemas.HabitCategory)
def create_category(category: schemas.HabitCategoryCreate, db: Session = Depends(get_db)):
    return crud.create_category(db=db, category=category)


@router.get("/records", response_model=list[schemas.HabitRecord])
def list_habit_records(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_habit_records(db=db, skip=skip, limit=limit)


@router.post("/records", response_model=schemas.HabitRecord)
def create_habit_record(record: schemas.HabitRecordCreate, db: Session = Depends(get_db)):
    return crud.create_habit_record(db=db, record=record)
