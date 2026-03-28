import uuid
from datetime import date
from sqlalchemy import String, Boolean, Date, ForeignKey, Text, Enum as SAEnum, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.mixins import TimestampSoftDeleteMixin
from app.models.enums import BillingCycle

class Expense(Base, TimestampSoftDeleteMixin):
    __tablename__ = "expenses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)

    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    billing_cycle: Mapped[BillingCycle] = mapped_column(
        SAEnum(BillingCycle, name="billing_cycle"),
        nullable=False,
        default=BillingCycle.monthly,
    )

    next_billing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    contract_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    auto_renewal: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    is_fixed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_subscription: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_review_target: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    auto_cancel_suggestion: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    manual_cancel_suggestion: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    cancel_suggestion: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    cancel_suggestion_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    memo: Mapped[str | None] = mapped_column(Text, nullable=True)

    category = relationship("Category", back_populates="expenses")
    user = relationship("User", back_populates="expenses", foreign_keys=[user_id])
