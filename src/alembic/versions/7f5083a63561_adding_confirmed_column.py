"""adding confirmed column

Revision ID: 7f5083a63561
Revises: 3068f03fe84f
Create Date: 2024-07-03 23:32:29.320384

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f5083a63561'
down_revision: Union[str, None] = '3068f03fe84f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("confirmed", sa.Boolean(), nullable=False))


def downgrade() -> None:
    op.drop_column("users", sa.Column("confirmed", sa.Boolean(), nullable=False))
