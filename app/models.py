import uuid
from enum import Enum as PyEnum

from sqlalchemy import (
    Column,
    String,
    Integer,
    DECIMAL,
    ForeignKey,
    Enum,
    Table,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base

class Country(Base):
    __tablename__ = "countries"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name = Column(
        String(100),
        unique=True,
        nullable=False
    )

    # relationship to Region
    regions = relationship(
        'Region',
        back_populates='country',
        cascade='all, delete-orphan'
    )


class Region(Base):
    __tablename__ = "regions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name = Column(
        String(100),
        nullable=False
    )
    country_id = Column(
        UUID(as_uuid=True),
        ForeignKey('countries.id'),
        nullable=False
    )

    # link back to Country
    country = relationship(
        'Country',
        back_populates='regions'
    )
    
    subregions = relationship(
        'Subregion',
        back_populates='region',
        cascade='all, delete-orphan'
    )

    __table_args__ = (
        UniqueConstraint('name', 'country_id', name='uix_region_name_country'),
    )


class Subregion(Base):
    __tablename__ = "subregions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name = Column(
        String(100),
        nullable=False
    )
    region_id = Column(
        UUID(as_uuid=True),
        ForeignKey('regions.id'),
        nullable=False
    )

    # link back to Region
    region = relationship(
        'Region',
        back_populates='subregions'
    )

    __table_args__ = (
        UniqueConstraint('name', 'region_id', name='uix_subregion_name_region'),
    )