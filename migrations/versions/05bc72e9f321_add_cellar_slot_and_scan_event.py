"""Add cellar_slot and scan_event

Revision ID: 05bc72e9f321
Revises: ccb231184f66
Create Date: 2025-07-05 15:24:55.988578

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '05bc72e9f321'
down_revision: Union[str, Sequence[str], None] = 'ccb231184f66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass

def downgrade() -> None:
    """Downgrade schema."""
    pass
