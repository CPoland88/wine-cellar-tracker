"""Add region and subregion models and CRUD endpoints

Revision ID: 223ba791d3b0
Revises: 584babc1833b
Create Date: 2025-07-03 13:35:23.698818

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '223ba791d3b0'
down_revision: Union[str, Sequence[str], None] = '584babc1833b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
