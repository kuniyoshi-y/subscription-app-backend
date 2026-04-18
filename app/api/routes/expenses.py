import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db, get_current_user_id
from app.models.category import Category
from app.models.expense import Expense
from app.models.enums import CategoryType
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseRead

router = APIRouter(prefix="/expenses", tags=["expenses"])


def _flags_from_category_type(category_type: CategoryType) -> dict:
    """カテゴリ種別に応じたフラグを返す"""
    if category_type == CategoryType.fixed:
        return {"is_fixed": True, "is_subscription": False, "is_review_target": False}
    if category_type == CategoryType.subscription:
        return {"is_fixed": False, "is_subscription": True, "is_review_target": True}
    # semi_fixed
    return {"is_fixed": False, "is_subscription": True, "is_review_target": True}

@router.get("", response_model=list[ExpenseRead])
def list_expenses(
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    rows = (
        db.execute(
            select(Expense)
            .where(Expense.user_id == user_id)
            .where(Expense.deleted_at.is_(None))
            .order_by(Expense.id.desc())
        )
        .scalars()
        .all()
    )
    return rows


@router.get("/{expense_id}", response_model=ExpenseRead)
def get_expense(
    expense_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    obj = db.get(Expense, expense_id)
    if not obj or obj.deleted_at is not None or obj.user_id != user_id:
        raise HTTPException(status_code=404, detail="Expense not found")
    return obj

@router.post("", response_model=ExpenseRead)
def create_expense(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    category = db.get(Category, payload.category_id)
    if not category or category.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Category not found")

    data = payload.model_dump()
    data["user_id"] = user_id
    # カテゴリ種別からフラグを自動セット（ペイロードの値より優先）
    data.update(_flags_from_category_type(category.type))

    obj = Expense(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.patch("/{expense_id}", response_model=ExpenseRead)
def update_expense(
    expense_id: uuid.UUID,
    payload: ExpenseUpdate,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    obj = db.get(Expense, expense_id)
    if not obj or obj.deleted_at is not None or obj.user_id != user_id:
        raise HTTPException(status_code=404, detail="Expense not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        if k == "user_id":
            continue
        setattr(obj, k, v)

    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{expense_id}")
def delete_expense(
    expense_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    obj = db.get(Expense, expense_id)
    if not obj or obj.deleted_at is not None or obj.user_id != user_id:
        raise HTTPException(status_code=404, detail="Expense not found")

    obj.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return {"ok": True}
