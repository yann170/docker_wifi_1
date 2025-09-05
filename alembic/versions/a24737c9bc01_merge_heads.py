"""merge heads

Revision ID: a24737c9bc01
Revises: ae72b0e4f27d, e081c471b6fb
Create Date: 2025-09-03 16:13:04.323645

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a24737c9bc01'
down_revision: Union[str, Sequence[str], None] = ('ae72b0e4f27d', 'e081c471b6fb')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
