from datetime import date

from pydantic import BaseModel, Field


class HabitCategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class HabitCategoryCreate(HabitCategoryBase):
    pass


class HabitCategory(HabitCategoryBase):
    id: int

    class Config:
        from_attributes = True


class HabitRecordBase(BaseModel):
    record_date: date
    habit_name: str = Field(min_length=1, max_length=100)
    category_id: int = Field(gt=0)
    completed: bool
    duration_minutes: int | None = Field(default=None, ge=0)
    notes: str | None = None


class HabitRecordCreate(HabitRecordBase):
    pass


class HabitRecord(HabitRecordBase):
    id: int

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class Token(BaseModel):
    access_token: str
    token_type: str
