import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, SmallInteger, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class UsageLog(Base):
    __tablename__ = "usage_logs"
    __table_args__ = (
        UniqueConstraint("expense_id", "month", name="uq_usage_logs_expense_month"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    expense_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("expenses.id"), nullable=False
    )
    month: Mapped[date] = mapped_column(Date, nullable=False)

    usage_status_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usage_statuses.id"), nullable=False
    )

    # 満足度 1〜5（未入力はNULL）
    rating: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    # スキップ（ユーザーが「今月は評価しない」と意思表示）
    is_skipped: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    expense = relationship("Expense", back_populates="usage_logs")
    usage_status = relationship("UsageStatus", back_populates="usage_logs")
