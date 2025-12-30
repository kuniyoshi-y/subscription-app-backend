import uuid
from datetime import date
from pydantic import BaseModel
from app.models.enums import BillingCycle


class ExpenseCreate(BaseModel):
    user_id: uuid.UUID
    name: str
    category_id: int
    amount: float
    billing_cycle: BillingCycle = BillingCycle.monthly
    next_billing_date: date | None = None
    contract_start_date: date | None = None
    auto_renewal: bool = True
    is_fixed: bool = False
    is_subscription: bool = True
    is_review_target: bool = True
    auto_cancel_suggestion: bool = False
    manual_cancel_suggestion: bool | None = None
    cancel_suggestion: bool = False
    cancel_suggestion_reason: str | None = None
    memo: str | None = None


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
    cancel_suggestion: bool

    class Config:
        from_attributes = True
