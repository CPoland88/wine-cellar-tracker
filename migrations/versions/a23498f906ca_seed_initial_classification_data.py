"""Seed initial classification data

Revision ID: a23498f906ca
Revises: 5000d139b044
Create Date: 2025-07-03 15:03:46.715177

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision: str = 'a23498f906ca'
down_revision: Union[str, Sequence[str], None] = '5000d139b044'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Insert country-level classifications
    op.execute(f"""
        INSERT INTO classifications (id, name, country_id, region_id)
        SELECT '{uuid.uuid4()}', 'AOC', id, NULL FROM countries WHERE name = 'France';
    """)
    op.execute(f"""
        INSERT INTO classifications (id, name, country_id, region_id)
        SELECT '{uuid.uuid4()}', 'IGP', id, NULL FROM countries WHERE name = 'France';
    """)
    op.execute(f"""
        INSERT INTO classifications (id, name, country_id, region_id)
        SELECT '{uuid.uuid4()}', 'Vin de France', id, NULL FROM countries WHERE name = 'France';
    """)

    # Burgundy & Champagne (region-scoped)
    op.execute(f"""
        INSERT INTO classifications (id, name, country_id, region_id)
        SELECT '{uuid.uuid4()}', 'Grand Cru', c.id, r.id
            FROM countries c JOIN regions r 
                ON c.id = r.country_id
            WHERE c.name = 'France' AND r.name = 'Burgundy & Champagne';
    """)
    op.execute(f"""
      INSERT INTO classifications (id, name, country_id, region_id)
      SELECT '{uuid.uuid4()}', 'Premier Cru', c.id, r.id
      FROM countries c JOIN regions r 
        ON c.id = r.country_id
      WHERE c.name = 'France' AND r.name = 'Burgundy & Champagne';
    """)
    op.execute(f"""
      INSERT INTO classifications (id, name, country_id, region_id)
      SELECT '{uuid.uuid4()}', 'Village', c.id, r.id
      FROM countries c JOIN regions r 
        ON c.id = r.country_id
      WHERE c.name = 'France' AND r.name = 'Burgundy & Champagne';
    """)
    op.execute(f"""
      INSERT INTO classifications (id, name, country_id, region_id)
      SELECT '{uuid.uuid4()}', 'Regional', c.id, r.id
      FROM countries c JOIN regions r 
        ON c.id = r.country_id
      WHERE c.name = 'France' AND r.name = 'Burgundy & Champagne';
    """)

    # Italy
    op.execute(f"""
      INSERT INTO classifications (id, name, country_id, region_id)
      SELECT '{uuid.uuid4()}', 'DOCG', id, NULL FROM countries WHERE name = 'Italy';
    """)
    op.execute(f"""
      INSERT INTO classifications (id, name, country_id, region_id)
      SELECT '{uuid.uuid4()}', 'DOC', id, NULL FROM countries WHERE name = 'Italy';
    """)
    op.execute(f"""
      INSERT INTO classifications (id, name, country_id, region_id)
      SELECT '{uuid.uuid4()}', 'IGT', id, NULL FROM countries WHERE name = 'Italy';
    """)
    op.execute(f"""
      INSERT INTO classifications (id, name, country_id, region_id)
      SELECT '{uuid.uuid4()}', 'VdT', id, NULL FROM countries WHERE name = 'Italy';
    """)

    # Spain & Portugal
    op.execute(f"""
      INSERT INTO classifications (id, name, country_id, region_id)
      SELECT '{uuid.uuid4()}', 'DOCa', id, NULL FROM countries WHERE name = 'Spain';
    """)
    op.execute(f"""
      INSERT INTO classifications (id, name, country_id, region_id)
      SELECT '{uuid.uuid4()}', 'DO', id, NULL FROM countries WHERE name = 'Spain';
    """)
    op.execute(f"""
      INSERT INTO classifications (id, name, country_id, region_id)
      SELECT '{uuid.uuid4()}', 'VdlT', id, NULL FROM countries WHERE name = 'Spain';
    """)
    op.execute(f"""
      INSERT INTO classifications (id, name, country_id, region_id)
      SELECT '{uuid.uuid4()}', 'Vinho Regional', id, NULL FROM countries WHERE name = 'Portugal';
    """)

    # Germany & Austria
    op.execute(f"""
      INSERT INTO classifications (id, name, country_id, region_id)
      SELECT '{uuid.uuid4()}', 'Prädikatswein', id, NULL FROM countries WHERE name = 'Germany';
    """)
    op.execute(f"""
      INSERT INTO classifications (id, name, country_id, region_id)
      SELECT '{uuid.uuid4()}', 'QbA', id, NULL FROM countries WHERE name = 'Germany';
    """)
    op.execute(f"""
      INSERT INTO classifications (id, name, country_id, region_id)
      SELECT '{uuid.uuid4()}', 'Landwein', id, NULL FROM countries WHERE name = 'Germany';
    """)
    op.execute(f"""
      INSERT INTO classifications (id, name, country_id, region_id)
      SELECT '{uuid.uuid4()}', 'Tafelwein', id, NULL FROM countries WHERE name = 'Germany';
    """)
    op.execute(f"""
      INSERT INTO classifications (id, name, country_id, region_id)
      SELECT '{uuid.uuid4()}', 'DAC', id, NULL FROM countries WHERE name = 'Austria';
    """)

    # New World & Other (global‐scoped)
    for name in ['AVA', 'GI', 'PDO', 'PGI', 'Unclassified']:
        op.execute(f"""
          INSERT INTO classifications (id, name, country_id, region_id)
          VALUES ('{uuid.uuid4()}','{name}', NULL, NULL);
        """)


def downgrade():
    # Delete all seeded rows
    op.execute("DELETE FROM classifications;")
