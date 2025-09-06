from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel
import sqlmodel.sql.sqltypes


revision: str = 'c12f0c4ff16a'
down_revision: Union[str, Sequence[str], None] = 'a24737c9bc01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('package', sa.Column('statut', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    op.add_column('transaction', sa.Column('statut', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    op.add_column('voucher', sa.Column('statut', sqlmodel.sql.sqltypes.AutoString(), nullable=False))

def downgrade() -> None:
    op.drop_column('voucher', 'statut')
    op.drop_column('transaction', 'statut')
    op.drop_column('package', 'statut')
    
