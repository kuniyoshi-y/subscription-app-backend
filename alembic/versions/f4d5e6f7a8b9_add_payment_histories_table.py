"""add payment_histories table

Revision ID: f4d5e6f7a8b9
Revises: e3c4d5e6f7a8
Create Date: 2026-03-28 00:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'f4d5e6f7a8b9'
down_revision: Union[str, Sequence[str], None] = 'e3c4d5e6f7a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # billing_cycle enum はすでに存在するので create_type=False で参照のみ
    billing_cycle = postgresql.ENUM(
        'monthly', 'yearly', 'other',
        name='billing_cycle',
        create_type=False,
    )
    op.create_table(
        'payment_histories',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('expense_id', sa.UUID(), nullable=False),
        sa.Column('paid_date', sa.Date(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('billing_cycle_snapshot', billing_cycle, nullable=False),
        sa.Column('method', sa.String(length=50), nullable=True),
        sa.Column('memo', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['expense_id'], ['expenses.id'], name='fk_payment_histories_expense_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('expense_id', 'paid_date', name='uq_payment_histories_expense_paid_date'),
    )


def downgrade() -> None:
    op.drop_table('payment_histories')
