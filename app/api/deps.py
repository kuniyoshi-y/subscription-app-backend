import uuid
from collections.abc import Generator

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import get_current_claims
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
    claims: dict = Depends(get_current_claims),
) -> uuid.UUID:
    """JWTのclaimsからDBのユーザーIDを解決して返す。
    初回ログイン時はDBにユーザーを自動登録する（A5）。
    """
    sub: str = claims["sub"]
    email: str = claims.get("email", "")

    user = db.execute(
        select(User).where(User.cognito_sub == sub).where(User.deleted_at.is_(None))
    ).scalar_one_or_none()

    if not user:
        # 初回ログイン：DBにユーザーを自動登録
        user = User(
            cognito_sub=sub,
            email=email,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user.id
