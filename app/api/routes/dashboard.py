import uuid
from calendar import monthrange
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func, case

from app.api.deps import get_db, get_current_user_id
from app.models.expense import Expense
from app.models.category import Category
from app.models.enums import BillingCycle
from app.schemas.dashboard import (
    CancelCandidate,
    CategoryBreakdown,
    CategoryMonthlyAmount,
    DashboardSummary,
    MonthlyTrendItem,
    MonthlyTrendResponse,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary", response_model=DashboardSummary)
def summary(
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):

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

    # 解約候補リストを取得
    candidate_rows = db.execute(
        select(Expense)
        .where(Expense.user_id == user_id)
        .where(Expense.deleted_at.is_(None))
        .where(Expense.cancel_suggestion.is_(True))
        .order_by(Expense.amount.desc())
    ).scalars().all()

    cancel_candidate_list = [
        CancelCandidate(
            id=e.id,
            name=e.name,
            amount=float(e.amount),
            billing_cycle=e.billing_cycle,
            cancel_suggestion_reason=e.cancel_suggestion_reason,
        )
        for e in candidate_rows
    ]

    total_monthly_f = float(total_monthly)

    return DashboardSummary(
        user_id=user_id,
        total_monthly=total_monthly_f,
        total_yearly=total_monthly_f * 12,
        by_category=by_category,
        cancel_candidates=int(cancel_candidates),
        cancel_candidate_list=cancel_candidate_list,
    )


@router.get("/monthly_trend", response_model=MonthlyTrendResponse)
def monthly_trend(
    months: int = Query(default=6, ge=1, le=24, description="遡る月数（デフォルト6ヶ月）"),
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """月別支出推移（カテゴリ別）

    現在有効な支出から各月の金額を積み上げて返す。
    - monthly: 毎月そのまま計上
    - yearly : 月割り（÷12）で計上
    - other  : 毎月そのまま計上（MVP簡略化）
    """
    today = date.today()

    # 遡るN月分の (year, month) リストを生成（古い順）
    target_months: list[tuple[int, int]] = []
    for i in range(months - 1, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        target_months.append((y, m))

    # アクティブな支出をカテゴリ情報と一緒に取得
    rows = db.execute(
        select(Expense, Category)
        .join(Category, Expense.category_id == Category.id)
        .where(Expense.user_id == user_id)
        .where(Expense.deleted_at.is_(None))
        .where(Category.deleted_at.is_(None))
    ).all()

    # 月ごとの集計
    items: list[MonthlyTrendItem] = []
    for year, month in target_months:
        cat_totals: dict[int, dict] = {}

        for expense, category in rows:
            if expense.billing_cycle == BillingCycle.yearly:
                amount = float(expense.amount) / 12
            else:
                amount = float(expense.amount)

            if category.id not in cat_totals:
                cat_totals[category.id] = {
                    "category_id": category.id,
                    "category_name": category.name,
                    "amount": 0.0,
                }
            cat_totals[category.id]["amount"] += amount

        by_category = [
            CategoryMonthlyAmount(**v)
            for v in sorted(cat_totals.values(), key=lambda x: x["amount"], reverse=True)
        ]
        total = sum(c.amount for c in by_category)

        items.append(MonthlyTrendItem(year=year, month=month, total=total, by_category=by_category))

    return MonthlyTrendResponse(items=items)
