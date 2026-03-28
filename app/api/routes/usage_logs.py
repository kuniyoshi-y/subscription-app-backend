import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.dev_user import DEV_USER_ID
from app.models.expense import Expense
from app.models.usage_log import UsageLog
from app.schemas.usage_log import UsageLogRead, UsageLogUpsert
from app.services.cancel_suggestion import recalculate_cancel_suggestion

router = APIRouter(tags=["usage_logs"])


@router.get("/expenses/{expense_id}/usage_logs", response_model=list[UsageLogRead])
def list_usage_logs(expense_id: uuid.UUID, db: Session = Depends(get_db)):
    """指定サービスの利用状況ログ一覧（月の降順）"""
    expense = db.get(Expense, expense_id)
    if not expense or expense.deleted_at is not None or expense.user_id != DEV_USER_ID:
        raise HTTPException(status_code=404, detail="Expense not found")

    rows = (
        db.execute(
            select(UsageLog)
            .where(UsageLog.expense_id == expense_id)
            .order_by(UsageLog.month.desc())
        )
        .scalars()
        .all()
    )
    return rows


@router.post("/usage_logs", response_model=UsageLogRead)
def upsert_usage_log(payload: UsageLogUpsert, db: Session = Depends(get_db)):
    """利用状況ログの登録・更新（同月は上書き）"""
    expense = db.get(Expense, payload.expense_id)
    if not expense or expense.deleted_at is not None or expense.user_id != DEV_USER_ID:
        raise HTTPException(status_code=404, detail="Expense not found")

    # is_skipped=True のときは rating を強制クリア
    rating = None if payload.is_skipped else payload.rating

    existing = db.execute(
        select(UsageLog).where(
            UsageLog.expense_id == payload.expense_id,
            UsageLog.month == payload.month,
        )
    ).scalar_one_or_none()

    if existing:
        existing.usage_status_id = payload.usage_status_id
        existing.rating = rating
        existing.is_skipped = payload.is_skipped
        existing.updated_at = datetime.now(timezone.utc)
        log = existing
    else:
        log = UsageLog(
            expense_id=payload.expense_id,
            month=payload.month,
            usage_status_id=payload.usage_status_id,
            rating=rating,
            is_skipped=payload.is_skipped,
        )
        db.add(log)

    db.flush()
    # usage_log 保存後に解約候補を再計算
    recalculate_cancel_suggestion(payload.expense_id, db)
    db.commit()
    db.refresh(log)
    return log


@router.delete("/usage_logs/{log_id}")
def delete_usage_log(log_id: uuid.UUID, db: Session = Depends(get_db)):
    """利用状況ログの削除"""
    log = db.get(UsageLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="UsageLog not found")

    # 所有者チェック（ログからExpenseを辿る）
    expense = db.get(Expense, log.expense_id)
    if not expense or expense.user_id != DEV_USER_ID:
        raise HTTPException(status_code=404, detail="UsageLog not found")

    db.delete(log)
    db.commit()
    return {"ok": True}
