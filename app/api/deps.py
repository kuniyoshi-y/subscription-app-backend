import uuid
from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user_sub
from app.core.db import SessionLocal
from app.models.user import User


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_id(
    db: Session = Depends(get_db),
    sub: str = Depends(get_current_user_sub),
) -> uuid.UUID:
    """JWTのsubからDBのユーザーIDを解決して返す"""
    user = db.execute(
        select(User).where(User.cognito_sub == sub).where(User.deleted_at.is_(None))
    ).scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user.id
