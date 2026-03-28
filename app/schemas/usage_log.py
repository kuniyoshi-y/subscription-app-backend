import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class UsageLogUpsert(BaseModel):
    expense_id: uuid.UUID
    month: date
    usage_status_id: int = Field(..., ge=1, le=3)
    rating: int | None = Field(default=None, ge=1, le=5)
    is_skipped: bool = False


class UsageLogRead(BaseModel):
    id: uuid.UUID
    expense_id: uuid.UUID
    month: date
    usage_status_id: int
    rating: int | None
    is_skipped: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
