"""Alter cellar_slots.row to String

Revision ID: d928168c82e6
Revises: 291c5a501cb6
Create Date: 2025-07-06 15:00:01.163642

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd928168c82e6'
down_revision: Union[str, Sequence[str], None] = '291c5a501cb6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():     
    # Change 'row' from INTEGER → VARCHAR(10), casting existing values.
    op.alter_column(
        'cellar_slots',         
        'row',         
        existing_type=sa.Integer(),         
        type_=sa.String(length=10),         
        postgresql_using='row::text'     
    )
    
def downgrade():
    # Revert back from VARCHAR → INTEGER, casting text → integer.    
    op.alter_column(
        'cellar_slots',         
        'row',         
        existing_type=sa.String(length=10),         
        type_=sa.Integer(),         
        postgresql_using='row::integer'
    )