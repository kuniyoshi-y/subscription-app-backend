"""add users table

Revision ID: c1a2b3d4e5f6
Revises: a248bab446a2
Create Date: 2026-03-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c1a2b3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'a248bab446a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('cognito_sub', sa.String(length=64), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('role', sa.Enum('user', 'admin', name='user_role'), nullable=False, server_default='user'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cognito_sub'),
        sa.UniqueConstraint('email'),
    )

    # expenses.user_id に FK を追加
    op.create_foreign_key(
        'fk_expenses_user_id',
        'expenses', 'users',
        ['user_id'], ['id'],
    )

    # categories.user_id に FK を追加
    op.create_foreign_key(
        'fk_categories_user_id',
        'categories', 'users',
        ['user_id'], ['id'],
    )


def downgrade() -> None:
    op.drop_constraint('fk_categories_user_id', 'categories', type_='foreignkey')
    op.drop_constraint('fk_expenses_user_id', 'expenses', type_='foreignkey')
    op.drop_table('users')
    op.execute("DROP TYPE IF EXISTS user_role")
