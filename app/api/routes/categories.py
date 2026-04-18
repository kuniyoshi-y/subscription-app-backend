from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

import uuid

from app.api.deps import get_db, get_current_user_id
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryRead

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
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    category = Category(
        user_id=user_id,
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
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    obj = db.get(Category, category_id)
    if not obj or obj.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Category not found")

    # システム標準カテゴリは削除不可
    if obj.is_system_default:
        raise HTTPException(status_code=403, detail="System default category cannot be deleted")

    # 自分のカテゴリ以外は削除不可
    if obj.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    obj.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return {"ok": True}
