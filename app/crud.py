from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas


def get_categories(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.HabitCategory).offset(skip).limit(limit).all()


def get_category_by_id(db: Session, category_id: int):
    return db.query(models.HabitCategory).filter(models.HabitCategory.id == category_id).first()


def create_category(db: Session, category: schemas.HabitCategoryCreate):
    existing = db.query(models.HabitCategory).filter(models.HabitCategory.name == category.name).first()
    if existing:
        raise ValueError("Category name already exists.")

    db_category = models.HabitCategory(**category.model_dump())
    try:
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("Category name already exists.") from exc


def get_habit_records(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.HabitRecord).offset(skip).limit(limit).all()


def get_habit_record_by_id(db: Session, record_id: int):
    return db.query(models.HabitRecord).filter(models.HabitRecord.id == record_id).first()


def create_habit_record(db: Session, record: schemas.HabitRecordCreate):
    category = get_category_by_id(db=db, category_id=record.category_id)
    if not category:
        raise LookupError("Category does not exist.")

    db_entry = models.HabitRecord(**record.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry
