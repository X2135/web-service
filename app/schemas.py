"""Pydantic request/response schemas used by API routes."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class HabitCategoryBase(BaseModel):
    # Limit category name length to keep UI rendering and indexing predictable.
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class HabitCategoryCreate(HabitCategoryBase):
    pass


class HabitCategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None


class HabitCategory(HabitCategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class HabitRecordBase(BaseModel):
    # Allow missing duration for legacy/imported rows, but enforce non-negative values when provided.
    record_date: date
    habit_name: str = Field(min_length=1, max_length=100)
    category_id: int = Field(gt=0)
    completed: bool
    duration_minutes: int | None = Field(default=None, ge=0)
    notes: str | None = None


class HabitRecordCreate(HabitRecordBase):
    pass


class HabitRecordUpdate(BaseModel):
    record_date: date | None = None
    habit_name: str | None = Field(default=None, min_length=1, max_length=100)
    category_id: int | None = Field(default=None, gt=0)
    completed: bool | None = None
    duration_minutes: int | None = Field(default=None, ge=0)
    notes: str | None = None


class HabitRecord(HabitRecordBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    # Demo credential payload accepted by `/auth/login`.
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class Token(BaseModel):
    access_token: str
    token_type: str


class MessageResponse(BaseModel):
    detail: str


class ErrorResponse(BaseModel):
    detail: str
    code: str


class CategoryCount(BaseModel):
    category_id: int
    category_name: str
    count: int


class DailyTrendPoint(BaseModel):
    record_date: date
    total: int
    completed: int


class AnalyticsSummary(BaseModel):
    # Aggregated KPIs consumed by dashboard summary and insight sections.
    total_records: int
    completed_records: int
    completion_rate: float
    average_duration: float
    records_per_category: list[CategoryCount]
    daily_trend: list[DailyTrendPoint]
