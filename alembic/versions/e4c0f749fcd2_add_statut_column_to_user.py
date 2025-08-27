"""add statut column to user

Revision ID: e4c0f749fcd2
Revises: 4b79b4d13552
Create Date: 2025-08-25 11:57:52.667775

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'e4c0f749fcd2'
down_revision: Union[str, Sequence[str], None] = '4b79b4d13552'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('transaction', 'payment_method',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.add_column(
        'user',
        sa.Column('statut', sa.String(), nullable=False, server_default='active')
    )
    op.add_column(
        'user',
        sa.Column('role', sa.String(), nullable=False, server_default='user')
    )
