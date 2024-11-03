"""adding s&p and nasdaq flag to metadata table

Revision ID: d62ec0e0fc5a
Revises: 42720b6abd00
Create Date: 2024-08-22 18:18:20.280997

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd62ec0e0fc5a'
down_revision: Union[str, None] = '42720b6abd00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("metadata", sa.Column("is_sp_constituent", sa.Boolean(), nullable=True))
    op.add_column("metadata", sa.Column("is_nasdaq_constituent", sa.Boolean(), nullable=True))


def downgrade() -> None:
    pass
