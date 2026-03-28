from pydantic import BaseModel
import uuid

from app.models.enums import BillingCycle


class CategoryBreakdown(BaseModel):
    category_id: int
    category_name: str
    amount_monthly: float


class CancelCandidate(BaseModel):
    id: uuid.UUID
    name: str
    amount: float
    billing_cycle: BillingCycle
    cancel_suggestion_reason: str | None


class DashboardSummary(BaseModel):
    user_id: uuid.UUID
    total_monthly: float
    total_yearly: float
    by_category: list[CategoryBreakdown]
    cancel_candidates: int
    cancel_candidate_list: list[CancelCandidate]


# 月別推移グラフ用
class CategoryMonthlyAmount(BaseModel):
    category_id: int
    category_name: str
    amount: float


class MonthlyTrendItem(BaseModel):
    year: int
    month: int
    total: float
    by_category: list[CategoryMonthlyAmount]


class MonthlyTrendResponse(BaseModel):
    items: list[MonthlyTrendItem]
