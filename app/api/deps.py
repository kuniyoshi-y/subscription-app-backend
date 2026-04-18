import uuid
from collections.abc import Generator

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import SessionLocal
from app.models.user import User


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user_id(
    request: Request,
    db: Session = Depends(get_db),
) -> uuid.UUID:
    """JWTのclaimsからDBのユーザーIDを解決して返す。
    DEV_MODE=true のときは固定のdev userを返す（ローカル開発用）。
    初回ログイン時はDBにユーザーを自動登録する。
    """
    # ローカル開発用バイパス
    if settings.DEV_MODE:
        dev_id = uuid.UUID(settings.DEV_USER_ID)
        user = db.get(User, dev_id)
        if not user:
            user = User(
                id=dev_id,
                email="dev@example.com",
                name="Dev User",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user.id

    # 本番：JWTを検証してユーザーを解決
    from app.core.auth import verify_token
    from fastapi.security import HTTPBearer

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = auth_header.split(" ", 1)[1]
    claims = verify_token(token)

    sub: str = claims["sub"]
    email: str = claims.get("email", "")

    user = db.execute(
        select(User).where(User.cognito_sub == sub).where(User.deleted_at.is_(None))
    ).scalar_one_or_none()

    if not user:
        user = User(cognito_sub=sub, email=email)
        db.add(user)
        db.commit()
        db.refresh(user)

    return user.id
