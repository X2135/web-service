from sqlalchemy.orm import Session

from app import models, schemas


def get_categories(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.HabitCategory).offset(skip).limit(limit).all()


def create_category(db: Session, category: schemas.HabitCategoryCreate):
    db_category = models.HabitCategory(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def get_habit_records(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.HabitRecord).offset(skip).limit(limit).all()


def get_habit_record_by_id(db: Session, record_id: int):
    return db.query(models.HabitRecord).filter(models.HabitRecord.id == record_id).first()


def create_habit_record(db: Session, record: schemas.HabitRecordCreate):
    db_entry = models.HabitRecord(**record.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry
