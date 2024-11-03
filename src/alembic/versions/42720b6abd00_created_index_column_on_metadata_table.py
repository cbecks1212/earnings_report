"""Created index column on metadata table

Revision ID: 42720b6abd00
Revises: 7f5083a63561
Create Date: 2024-08-22 16:25:22.521328

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42720b6abd00'
down_revision: Union[str, None] = '7f5083a63561'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("metadata", sa.Column("index", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("metadata", 'index')
