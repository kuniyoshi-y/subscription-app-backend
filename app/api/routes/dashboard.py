import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func, case

from app.api.deps import get_db
from app.models.expense import Expense
from app.models.category import Category
from app.models.enums import BillingCycle
from app.schemas.dashboard import DashboardSummary, CategoryBreakdown

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary", response_model=DashboardSummary)
def summary(user_id: uuid.UUID, db: Session = Depends(get_db)):
    monthly_amount = case(
        (Expense.billing_cycle == BillingCycle.monthly, Expense.amount),
        (Expense.billing_cycle == BillingCycle.yearly, Expense.amount / 12),
        else_=Expense.amount,
    )

    total_monthly = db.execute(
        select(func.coalesce(func.sum(monthly_amount), 0))
        .where(Expense.user_id == user_id)
        .where(Expense.deleted_at.is_(None))
    ).scalar_one()

    cancel_candidates = db.execute(
        select(func.count())
        .select_from(Expense)
        .where(Expense.user_id == user_id)
        .where(Expense.deleted_at.is_(None))
        .where(Expense.cancel_suggestion.is_(True))
    ).scalar_one()

    rows = db.execute(
        select(
            Category.id.label("id"),
            Category.name.label("name"),
            func.coalesce(func.sum(monthly_amount), 0).label("amount_monthly"),
        )
        .join(Expense, Expense.category_id == Category.id)
        .where(Expense.user_id == user_id)
        .where(Expense.deleted_at.is_(None))
        .where(Category.deleted_at.is_(None))
        .group_by(Category.id, Category.name)
        .order_by(func.sum(monthly_amount).desc())
    ).all()

    by_category = [
        CategoryBreakdown(
            category_id=r.id,
            category_name=r.name,
            amount_monthly=float(r.amount_monthly),
        )
        for r in rows
    ]

    total_monthly_f = float(total_monthly)

    return DashboardSummary(
        user_id=user_id,
        total_monthly=total_monthly_f,
        total_yearly=total_monthly_f * 12,
        by_category=by_category,
        cancel_candidates=int(cancel_candidates),
    )
