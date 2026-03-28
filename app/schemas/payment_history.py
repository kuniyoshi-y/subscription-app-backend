import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.models.enums import BillingCycle


class PaymentHistoryCreate(BaseModel):
    expense_id: uuid.UUID
    paid_date: date
    amount: float
    billing_cycle_snapshot: BillingCycle
    method: str | None = None
    memo: str | None = None


class PaymentHistoryRead(BaseModel):
    id: uuid.UUID
    expense_id: uuid.UUID
    paid_date: date
    amount: float
    billing_cycle_snapshot: BillingCycle
    method: str | None
    memo: str | None
    created_at: datetime

    class Config:
        from_attributes = True
