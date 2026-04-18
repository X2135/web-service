from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app import crud, schemas
from app.database import get_db

router = APIRouter()


@router.get("/categories", response_model=list[schemas.HabitCategory])
def list_categories(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return crud.get_categories(db=db, skip=skip, limit=limit)


@router.get("/categories/{category_id}", response_model=schemas.HabitCategory)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = crud.get_category_by_id(db=db, category_id=category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")
    return category


@router.post("/categories", response_model=schemas.HabitCategory)
def create_category(
    category: schemas.HabitCategoryCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    try:
        return crud.create_category(db=db, category=category)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.put("/categories/{category_id}", response_model=schemas.HabitCategory)
def update_category(
    category_id: int,
    category: schemas.HabitCategoryUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    try:
        updated = crud.update_category(db=db, category_id=category_id, category=category)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")
    return updated


@router.delete("/categories/{category_id}", response_model=schemas.MessageResponse)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    deleted = crud.delete_category(db=db, category_id=category_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")
    return {"detail": "Category deleted successfully."}


@router.get("/records", response_model=list[schemas.HabitRecord])
def list_habit_records(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_habit_records(db=db, skip=skip, limit=limit)


@router.get("/records/{record_id}", response_model=schemas.HabitRecord)
def get_habit_record(record_id: int, db: Session = Depends(get_db)):
    record = crud.get_habit_record_by_id(db=db, record_id=record_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found.")
    return record


@router.post("/records", response_model=schemas.HabitRecord)
def create_habit_record(
    record: schemas.HabitRecordCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    try:
        return crud.create_habit_record(db=db, record=record)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.put("/records/{record_id}", response_model=schemas.HabitRecord)
def update_habit_record(
    record_id: int,
    record: schemas.HabitRecordUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    try:
        updated = crud.update_habit_record(db=db, record_id=record_id, record=record)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found.")
    return updated


@router.delete("/records/{record_id}", response_model=schemas.MessageResponse)
def delete_habit_record(
    record_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    deleted = crud.delete_habit_record(db=db, record_id=record_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found.")
    return {"detail": "Record deleted successfully."}
