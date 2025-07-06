"""Alter cellar_slots to int and str

Revision ID: 291c5a501cb6
Revises: 9d2842b9b497
Create Date: 2025-07-06 14:48:17.366916

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '291c5a501cb6'
down_revision: Union[str, Sequence[str], None] = '9d2842b9b497'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():     
    # Change rack from VARCHAR to INTEGER, casting existing data.    
    op.alter_column(
        'cellar_slots',         
        'rack',         
        existing_type=sa.String(length=50),         
        type_=sa.Integer(),         
        postgresql_using='rack::integer'
    )  
    
def downgrade():     
    # Revert back to String if you ever need.  
    op.alter_column(
        'cellar_slots',         
        'rack',         
        existing_type=sa.Integer(),         
        type_=sa.String(length=1),         
        postgresql_using='rack::text'
    ) 