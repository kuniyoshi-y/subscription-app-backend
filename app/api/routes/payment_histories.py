import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.dev_user import DEV_USER_ID
from app.models.expense import Expense
from app.models.payment_history import PaymentHistory
from app.schemas.payment_history import PaymentHistoryCreate, PaymentHistoryRead

router = APIRouter(tags=["payment_histories"])


@router.get("/expenses/{expense_id}/payment_histories", response_model=list[PaymentHistoryRead])
def list_payment_histories(
    expense_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """指定サービスの支払い履歴一覧（支払い日の降順）"""
    expense = db.get(Expense, expense_id)
    if not expense or expense.deleted_at is not None or expense.user_id != DEV_USER_ID:
        raise HTTPException(status_code=404, detail="Expense not found")

    rows = (
        db.execute(
            select(PaymentHistory)
            .where(PaymentHistory.expense_id == expense_id)
            .order_by(PaymentHistory.paid_date.desc())
        )
        .scalars()
        .all()
    )
    return rows


@router.get("/payment_histories", response_model=list[PaymentHistoryRead])
def list_payment_histories_by_month(
    year: int = Query(..., description="例: 2026"),
    month: int = Query(..., ge=1, le=12, description="例: 3"),
    db: Session = Depends(get_db),
):
    """月別の支払い履歴一覧（グラフ用）"""
    from calendar import monthrange
    last_day = monthrange(year, month)[1]
    from_date = date(year, month, 1)
    to_date = date(year, month, last_day)

    rows = (
        db.execute(
            select(PaymentHistory)
            .join(Expense, PaymentHistory.expense_id == Expense.id)
            .where(Expense.user_id == DEV_USER_ID)
            .where(Expense.deleted_at.is_(None))
            .where(PaymentHistory.paid_date >= from_date)
            .where(PaymentHistory.paid_date <= to_date)
            .order_by(PaymentHistory.paid_date.desc())
        )
        .scalars()
        .all()
    )
    return rows


@router.post("/payment_histories", response_model=PaymentHistoryRead)
def create_payment_history(payload: PaymentHistoryCreate, db: Session = Depends(get_db)):
    """支払い履歴の手動登録"""
    expense = db.get(Expense, payload.expense_id)
    if not expense or expense.deleted_at is not None or expense.user_id != DEV_USER_ID:
        raise HTTPException(status_code=404, detail="Expense not found")

    record = PaymentHistory(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/payment_histories/{history_id}")
def delete_payment_history(history_id: uuid.UUID, db: Session = Depends(get_db)):
    """支払い履歴の削除"""
    record = db.get(PaymentHistory, history_id)
    if not record:
        raise HTTPException(status_code=404, detail="PaymentHistory not found")

    expense = db.get(Expense, record.expense_id)
    if not expense or expense.user_id != DEV_USER_ID:
        raise HTTPException(status_code=404, detail="PaymentHistory not found")

    db.delete(record)
    db.commit()
    return {"ok": True}
