from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryRead
from app.core.dev_user import DEV_USER_ID

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    rows = (
        db.execute(select(Category).order_by(Category.sort_order, Category.id))
        .scalars()
        .all()
    )
    return rows


@router.post("", response_model=CategoryRead)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    category = Category(
        user_id=DEV_USER_ID,
        name=payload.name,
        type=payload.type,
    )

    db.add(category)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
    status_code=409,
    detail={"code": "CATEGORY_NAME_DUPLICATE", "message": "Category name already exists"},
)


    db.refresh(category)
    return category


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    obj = db.get(Category, category_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(obj)
    db.commit()
    return {"ok": True}
