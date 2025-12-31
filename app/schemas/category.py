from pydantic import BaseModel, Field
from app.models.enums import CategoryType

class CategoryCreate(BaseModel):
    name: str
    type: CategoryType = Field(
        default=CategoryType.subscription,
        description="カテゴリ種別（default: subscription）",
    )
    is_system_default: bool = False
    sort_order: int = 0

class CategoryRead(BaseModel):
    id: int
    name: str
    type: CategoryType          # ← enumにする
    is_system_default: bool
    sort_order: int

    class Config:
        from_attributes = True
