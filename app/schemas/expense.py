import uuid
from datetime import date, datetime
from pydantic import BaseModel
from app.models.enums import BillingCycle


class ExpenseCreate(BaseModel):
    name: str
    category_id: int
    amount: float
    billing_cycle: BillingCycle = BillingCycle.monthly
    next_billing_date: date | None = None
    contract_start_date: date | None = None
    auto_renewal: bool = True
    memo: str | None = None
    # is_fixed / is_subscription / is_review_target はカテゴリ連動で自動セット（T5）


class ExpenseUpdate(BaseModel):
    name: str | None = None
    category_id: int | None = None
    amount: float | None = None
    billing_cycle: BillingCycle | None = None
    next_billing_date: date | None = None
    contract_start_date: date | None = None

    auto_renewal: bool | None = None
    is_fixed: bool | None = None
    is_subscription: bool | None = None
    is_review_target: bool | None = None

    auto_cancel_suggestion: bool | None = None
    manual_cancel_suggestion: bool | None = None
    cancel_suggestion: bool | None = None

    cancel_suggestion_reason: str | None = None
    memo: str | None = None


class ExpenseRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    category_id: int
    amount: float
    billing_cycle: BillingCycle

    next_billing_date: date | None
    contract_start_date: date | None
    auto_renewal: bool

    is_fixed: bool
    is_subscription: bool
    is_review_target: bool

    auto_cancel_suggestion: bool
    manual_cancel_suggestion: bool | None
    cancel_suggestion: bool
    cancel_suggestion_reason: str | None

    memo: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
