"""add unique index for categories name per user

Revision ID: a248bab446a2
Revises: f63defb6430f
Create Date: 2025-12-31 19:02:05.198501

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'a248bab446a2'
down_revision: Union[str, Sequence[str], None] = 'f63defb6430f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "uq_categories_user_id_name_active",
        "categories",
        ["user_id", "name"],
        unique=True,
        postgresql_where=text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_categories_user_id_name_active", table_name="categories")
