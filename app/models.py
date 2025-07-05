import uuid
from enum import Enum as PyEnum
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Integer,
    DECIMAL,
    ForeignKey,
    Enum as SAEnum,
    Table,
    UniqueConstraint,
    Date,
    Numeric,
    DateTime
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base

# -- Enumerations for bottle size, closure ----------------------------
class BottleSize(PyEnum):
    PICCOLO = "piccolo"  # 187ml
    HALF = "small"  # 375ml
    STANDARD = "standard"  # 750ml
    MAGNUM = "magnum"  # 1500ml
    JEROBOAM = "jeroboam"  # 3000ml
    REHOBOAM = "rehoboam"  # 4500ml
    METHUSELAH = "methuselah"  # 6000ml
    SALMANAZAR = "salmanazar"  # 9000ml
    BALTHAZAR = "balthazar"  # 12000ml
    NEBUCHADNEZZAR = "nebuchadnezzar"  # 15000ml
    MELCHIOR = "melchior"  # 18000ml
    OTHER = "other"  # Any other size not listed

class ClosureType(PyEnum):
    CORK = "cork"
    SYNTHETIC = "synthetic"
    SCREW_CAP = "screw cap"
    CROWN_CAP = "crown cap"
    OTHER = "other"
# -------------------------------------------------------------

# -- Country, Region, Subregion models ----------------------------
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
# -------------------------------------------------------------

# -- Wine classification enums --------------------------------
class Classification(Base):
    __tablename__ = "classifications"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name = Column(String(100), nullable=False)

    # Scope columns - one or the other can be NULL for general classifications
    country_id = Column(UUID(as_uuid=True), ForeignKey('countries.id'), nullable=True)
    region_id = Column(UUID(as_uuid=True), ForeignKey('regions.id'), nullable=True)

    # Relationships back to the lookups
    country = relationship('Country', backref='classifications')
    region = relationship('Region', backref='classifications')

    __table_args__ = (
        # Prevent exact duplicates for the same scope
        UniqueConstraint('name', 'country_id', 'region_id',
                         name='uix_classification_name_scope'),
    )

# --- Varietal and Blend models -----------------------------
class Varietal(Base):
    __tablename__ = "varietals"

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

wine_varietals = Table(
    'wine_varietals',
    Base.metadata,
    Column(
        'wine_id',
        UUID(as_uuid=True),
        ForeignKey('wines.id'),
        primary_key=True
    ),
    Column(
        'varietal_id',
        UUID(as_uuid=True),
        ForeignKey('varietals.id'),
        primary_key=True
    ),
    Column(
        'blend_pct',
        DECIMAL(5, 2),
        nullable=False
    )
)

# --- Wine table format ---------------------------------
class Wine(Base):
    __tablename__ = "wines"
    
    # 1. Primary key and core identity
    id          = Column(UUID(as_uuid=True), primary_key=True,default=uuid.uuid4)
    producer    = Column(String(100), nullable=False)
    label       = Column(String(100), nullable=False)
    vintage     = Column(Integer, nullable=False)

    # 2. Geographic scope
    country_id      = Column(UUID(as_uuid=True), ForeignKey('countries.id'), nullable=False)
    region_id       = Column(UUID(as_uuid=True), ForeignKey('regions.id'), nullable=False)
    subregion_id    = Column(UUID(as_uuid=True), ForeignKey('subregions.id'), nullable=False)
    
    # 3. Classification lookup
    classification_id = Column(UUID(as_uuid=True), ForeignKey('classifications.id'), nullable=True)

    # 4. Physical attributes
    bottle_size     = Column(SAEnum(BottleSize), nullable=False)
    closure_type    = Column(SAEnum(ClosureType), nullable=False)
    abv             = Column(DECIMAL(4,2), nullable=True)

    # 5. Relationships
    country         = relationship('Country')
    region          = relationship('Region')
    subregion       = relationship('Subregion')
    classification  = relationship('Classification')
    varietals       = relationship('Varietal', secondary='wine_varietals', backref='wines')

    # 6. Uniqueness: no duplicate producer/label/vintage/size combos
    __table_args__ = (
        UniqueConstraint('producer', 'label', 'vintage', 'bottle_size', name='uix_wine_unique'),
    )

# ---- Purchase price and timing --------------------------
class Purchase(Base):
    __tablename__ = 'purchases'

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wine_id         = Column(UUID(as_uuid=True),ForeignKey('wines.id'), nullable=False)
    purchase_date   = Column(Date, nullable=False)
    price_amount    = Column(Numeric(10,2), nullable=False)
    price_currency  = Column(String(3), nullable=False)     # ISO currency code, e.g., "USD"
    receipt_url     = Column(String(500), nullable=True)    # link or photo URL

    wine = relationship('Wine', backref='purchases')


# --- Critic & Quality metrics ----------------------------
class CriticScore(Base):
    __tablename__ = 'critic_scores'

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wine_id     = Column(UUID(as_uuid=True), ForeignKey('wines.id'), nullable=False)
    source      = Column(String(100), nullable=False)   # e.g., "WA", "Decanter"
    score       = Column(DECIMAL(5,2), nullable=False)  # e.g., 96.00
    review_date = Column(Date, nullable=True)

    wine = relationship('Wine', backref='critic_scores')

class WineMetrics(Base):
    __tablename__ = 'wine_metrics'

    wine_id         = Column(UUID(as_uuid=True), ForeignKey('wines.id'), primary_key=True)
    avg_score       = Column(DECIMAL(5,2), nullable=True)
    review_count    = Column(Integer, nullable=False, default=0)
    current_market  = Column(Numeric(10,2), nullable=True)
    rarity_score    = Column(DECIMAL(5,2), nullable=True)
    qpr             = Column(DECIMAL(5,2), nullable=True)

    wine = relationship('Wine', backref='metrics', uselist=False)


# --- Cellar slot for physical bottle locations ---------------
class CellarSlot(Base):
    __tablename__ = 'cellar_slots'

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rack        = Column(String(50), nullable=False)
    row         = Column(Integer, nullable=False)
    led_node_id = Column(String(100), nullable=False)

    __table_args__ = (UniqueConstraint('rack', 'row', name='uix_slot_location'),)


# --- In-Out Enum for scan events --------------------------
class EventTypeEnum(PyEnum):
    IN = "in"
    OUT = "out"

# --- ScanEvent to log slotting/unslotting events ------------
class ScanEvent(Base):
    __tablename__ = 'scan_events'

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wine_id     = Column(UUID(as_uuid=True), ForeignKey('wines.id'), nullable=False)
    slot_id     = Column(UUID(as_uuid=True), ForeignKey('cellar_slots.id'), nullable=False)
    event_type  = Column(SAEnum(EventTypeEnum), nullable=False)
    timestamp   = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships for easy access
    wine = relationship('Wine', backref='scan_events')
    slot = relationship('CellarSlot', backref='scan_events')