from sqlalchemy import case, func
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


def get_analytics_summary(db: Session):
    # Run aggregations at the database layer to avoid loading all records into application memory.
    total_records = db.query(func.count(models.HabitRecord.id)).scalar() or 0
    completed_records = (
        db.query(func.count(models.HabitRecord.id))
        .filter(models.HabitRecord.completed.is_(True))
        .scalar()
        or 0
    )

    avg_duration = db.query(func.avg(models.HabitRecord.duration_minutes)).scalar()
    average_duration = float(avg_duration or 0.0)

    category_rows = (
        db.query(
            models.HabitCategory.id,
            models.HabitCategory.name,
            func.count(models.HabitRecord.id),
        )
        .outerjoin(models.HabitRecord, models.HabitRecord.category_id == models.HabitCategory.id)
        .group_by(models.HabitCategory.id, models.HabitCategory.name)
        .order_by(models.HabitCategory.name.asc())
        .all()
    )

    records_per_category = [
        {
            "category_id": row[0],
            "category_name": row[1],
            "count": row[2],
        }
        for row in category_rows
    ]

    trend_rows = (
        db.query(
            models.HabitRecord.record_date,
            func.count(models.HabitRecord.id),
            func.sum(case((models.HabitRecord.completed.is_(True), 1), else_=0)),
        )
        .group_by(models.HabitRecord.record_date)
        .order_by(models.HabitRecord.record_date.asc())
        .all()
    )

    daily_trend = [
        {
            "record_date": row[0],
            "total": int(row[1] or 0),
            "completed": int(row[2] or 0),
        }
        for row in trend_rows
    ]

    completion_rate = round((completed_records / total_records) * 100, 2) if total_records else 0.0

    return {
        "total_records": total_records,
        "completed_records": completed_records,
        "completion_rate": completion_rate,
        "average_duration": round(average_duration, 2),
        "records_per_category": records_per_category,
        "daily_trend": daily_trend,
    }


def check_seed_applied(db: Session, seed_name: str) -> bool:
    return db.query(models.SeedHistory).filter(models.SeedHistory.seed_name == seed_name).first() is not None


def mark_seed_applied(db: Session, seed_name: str):
    db_seed = models.SeedHistory(seed_name=seed_name)
    try:
        db.add(db_seed)
        db.commit()
        db.refresh(db_seed)
        return db_seed
    except IntegrityError as exc:
        db.rollback()
        raise ValueError(f"Seed '{seed_name}' already exists.") from exc
