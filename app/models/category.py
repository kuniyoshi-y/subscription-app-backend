from sqlalchemy import String, Boolean, Integer, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import Base
from app.models.enums import CategoryType
from app.models.mixins import TimestampSoftDeleteMixin

class Category(Base, TimestampSoftDeleteMixin):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    type: Mapped[CategoryType] = mapped_column(
        SAEnum(CategoryType, name="category_type"),
        nullable=False,
    )

    is_system_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    expenses = relationship("Expense", back_populates="category")
    user = relationship("User", back_populates="categories", foreign_keys=[user_id])
