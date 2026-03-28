import uuid
from datetime import datetime

from sqlalchemy import String, Enum as SAEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import UserRole
from app.models.mixins import TimestampSoftDeleteMixin


class User(Base, TimestampSoftDeleteMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Cognito連携用（現時点はnullable、Cognito実装時に必須化）
    cognito_sub: Mapped[str | None] = mapped_column(
        String(64), unique=True, nullable=True
    )

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"),
        nullable=False,
        default=UserRole.user,
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    expenses = relationship("Expense", back_populates="user", foreign_keys="Expense.user_id")
    categories = relationship("Category", back_populates="user", foreign_keys="Category.user_id")
