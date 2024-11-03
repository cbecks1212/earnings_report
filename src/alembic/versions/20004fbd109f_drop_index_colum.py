"""drop index colum

Revision ID: 20004fbd109f
Revises: d62ec0e0fc5a
Create Date: 2024-08-22 18:55:48.019296

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20004fbd109f'
down_revision: Union[str, None] = 'd62ec0e0fc5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('metadata', 'index')


def downgrade() -> None:
    pass
