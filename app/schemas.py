from datetime import date

from pydantic import BaseModel


class HabitCategoryBase(BaseModel):
    name: str
    description: str | None = None


class HabitCategoryCreate(HabitCategoryBase):
    pass


class HabitCategory(HabitCategoryBase):
    id: int

    class Config:
        from_attributes = True


class HabitRecordBase(BaseModel):
    record_date: date
    habit_name: str
    category_id: int
    completed: bool
    duration_minutes: int | None = None
    notes: str | None = None


class HabitRecordCreate(HabitRecordBase):
    pass


class HabitRecord(HabitRecordBase):
    id: int

    class Config:
        from_attributes = True
