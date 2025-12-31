from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.api.deps import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryRead

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    rows = db.execute(select(Category).order_by(Category.sort_order, Category.id)).scalars().all()
    return rows

@router.post("", response_model=CategoryRead)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    obj = Category(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    obj = db.get(Category, category_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
