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


def update_category(db: Session, category_id: int, category: schemas.HabitCategoryUpdate):
    db_category = get_category_by_id(db=db, category_id=category_id)
    if not db_category:
        return None

    update_data = category.model_dump(exclude_unset=True)
    if "name" in update_data:
        existing = db.query(models.HabitCategory).filter(models.HabitCategory.name == update_data["name"]).first()
        if existing and existing.id != category_id:
            raise ValueError("Category name already exists.")

    for field, value in update_data.items():
        setattr(db_category, field, value)

    try:
        db.commit()
        db.refresh(db_category)
        return db_category
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("Category name already exists.") from exc


def delete_category(db: Session, category_id: int):
    db_category = get_category_by_id(db=db, category_id=category_id)
    if not db_category:
        return None

    db.delete(db_category)
    db.commit()
    return db_category


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


def update_habit_record(db: Session, record_id: int, record: schemas.HabitRecordUpdate):
    db_record = get_habit_record_by_id(db=db, record_id=record_id)
    if not db_record:
        return None

    update_data = record.model_dump(exclude_unset=True)
    if "category_id" in update_data:
        category = get_category_by_id(db=db, category_id=update_data["category_id"])
        if not category:
            raise LookupError("Category does not exist.")

    for field, value in update_data.items():
        setattr(db_record, field, value)

    db.commit()
    db.refresh(db_record)
    return db_record


def delete_habit_record(db: Session, record_id: int):
    db_record = get_habit_record_by_id(db=db, record_id=record_id)
    if not db_record:
        return None

    db.delete(db_record)
    db.commit()
    return db_record
