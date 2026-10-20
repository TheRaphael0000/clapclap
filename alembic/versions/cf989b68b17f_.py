"""empty message

Revision ID: cf989b68b17f
Revises: bbe3b2e3d49a
Create Date: 2026-10-20 18:22:22.085503

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf989b68b17f'
down_revision: Union[str, Sequence[str], None] = 'bbe3b2e3d49a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
