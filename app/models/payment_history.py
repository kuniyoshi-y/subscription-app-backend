import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum as SAEnum, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import BillingCycle


class PaymentHistory(Base):
    __tablename__ = "payment_histories"
    __table_args__ = (
        UniqueConstraint("expense_id", "paid_date", name="uq_payment_histories_expense_paid_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    expense_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("expenses.id"), nullable=False
    )

    paid_date: Mapped[date] = mapped_column(Date, nullable=False)

    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # 支払い当時の課金周期スナップショット（過去が変わらないように保持）
    billing_cycle_snapshot: Mapped[BillingCycle] = mapped_column(
        SAEnum(BillingCycle, name="billing_cycle"),
        nullable=False,
    )

    method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    memo: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    expense = relationship("Expense", back_populates="payment_histories")
