from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.api.deps import get_db
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseRead
from app.core.dev_user import DEV_USER_ID
import uuid

router = APIRouter(prefix="/expenses", tags=["expenses"])

@router.get("", response_model=list[ExpenseRead])
def list_expenses(db: Session = Depends(get_db)):
    rows = (
        db.execute(
            select(Expense)
            .where(Expense.user_id == DEV_USER_ID)
            .order_by(Expense.id.desc())
        )
        .scalars()
        .all()
    )
    return rows

@router.get("/{expense_id}", response_model=ExpenseRead)
def get_expense(expense_id: uuid.UUID, db: Session = Depends(get_db)):
    obj = db.get(Expense, expense_id)
    if not obj or obj.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return obj

@router.post("", response_model=ExpenseRead)
def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    data["user_id"] = DEV_USER_ID
    obj = Expense(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.patch("/{expense_id}", response_model=ExpenseRead)
def update_expense(expense_id: int, payload: ExpenseUpdate, db: Session = Depends(get_db)):
    obj = db.get(Expense, expense_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Expense not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)

    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    obj = db.get(Expense, expense_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
