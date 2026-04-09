from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class HabitCategory(Base):
    __tablename__ = "habit_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)

    records = relationship("HabitRecord", back_populates="category")


class HabitRecord(Base):
    __tablename__ = "habit_records"

    id = Column(Integer, primary_key=True, index=True)
    record_date = Column(Date, nullable=False)
    habit_name = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("habit_categories.id"), nullable=False)
    completed = Column(Boolean, nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)

    category = relationship("HabitCategory", back_populates="records")
