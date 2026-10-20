"""merge conflicting heads

Revision ID: bbe3b2e3d49a
Revises: edfa0010292f
Create Date: 2026-10-20 18:21:56.677069

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bbe3b2e3d49a'
down_revision: Union[str, Sequence[str], None] = 'edfa0010292f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
