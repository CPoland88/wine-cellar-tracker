from pydantic import BaseModel, UUID4, condecimal, constr
from typing import Optional, List
from app.models import BottleSize, ClosureType
from datetime import date, datetime

from app.models import EventTypeEnum

# --- Country Schemas -----------------------------
class CountryBase(BaseModel):
    name: str

class CountryCreate(CountryBase):
    """Inputs for creating a country."""
    pass

class CountryRead(CountryBase):
    """Response model for returning country data."""
    id: UUID4

    class Config:
        orm_mode = True


# --- Region Schemas ------------------------------
class RegionBase(BaseModel):
    name: str
    country_id: UUID4  

class RegionCreate(RegionBase):
    """Inputs for creating a region."""
    pass

class RegionRead(RegionBase):
    """Response model for returning region data with nested country."""
    id: UUID4
    country: CountryRead

    class Config:
        orm_mode = True


# --- Subregion Schemas ---------------------------
class SubregionBase(BaseModel):
    name: str
    region_id: UUID4

class SubregionCreate(SubregionBase):
    """Inputs for creating a subregion."""
    pass

class SubregionRead(SubregionBase):
    """Response model for returning subregion data with nested region."""
    id: UUID4
    region: RegionRead

    class Config:
        orm_mode = True

# --- Classification Schemas ----------------------
class ClassificationBase(BaseModel):
    name: str
    country_id: Optional[UUID4]
    region_id: Optional[UUID4]

class ClassificationCreate(ClassificationBase):
    pass

class ClassificationRead(ClassificationBase):
    id: UUID4

    class Config:
        orm_mode = True

# --- Varietal Schemas ---------------------------
class VarietalBase(BaseModel):
    name: str

class VarietalCreate(VarietalBase):
    """Input when creating a new varietal."""
    pass

class VarietalRead(VarietalBase):
    """Response model for returning varietal data."""
    id: UUID4

    class Config:
        orm_mode = True

# —-- Wine Schemas ———————————————————————————————-
class WineBase(BaseModel):
    producer: str
    label: str
    vintage: int
    country_id: UUID4
    region_id: UUID4
    subregion_id: Optional[UUID4] = None
    classification_id: Optional[UUID4] = None
    bottle_size: BottleSize
    closure_type: ClosureType
    abv: Optional[condecimal(max_digits=4, decimal_places=2)] = None

class WineCreate(WineBase):
    """Fields required to create a new wine."""
    pass

class WineRead(WineBase):
    """Fields returned when reading a wine, including ID and nested lookups."""
    id: UUID4
    country: CountryRead
    region: RegionRead
    subregion: Optional[SubregionRead] = None
    classification: Optional[ClassificationRead] = None
    varietals: List[VarietalRead] = []

    class Config:
        orm_mode = True


# --- Purchase schemas ---------------------------
class PurchaseBase(BaseModel):
    wine_id: UUID4
    purchase_date: date
    price_amount: condecimal(max_digits=10, decimal_places=2)
    price_currency: constr(min_length=3, max_length=3)
    receipt_url: Optional[str] = None

class PurchaseCreate(PurchaseBase):
    pass

class PurchaseRead(PurchaseBase):
    id: UUID4
    wine: WineRead  # nested

    class Config:
        orm_mode = True


# --- Critic and Qualtiy metric schemas ------------
class CriticScoreBase(BaseModel):
    wine_id: UUID4
    source: str
    score: condecimal(max_digits=5, decimal_places=2)
    review_date: Optional[date]

class CriticScoreCreate(CriticScoreBase):
    pass 

class CriticScoreRead(CriticScoreBase):
    id: UUID4

    class Config:
        orm_mode = True

class WineMetricsRead(BaseModel):
    wine_id: UUID4
    avg_score: Optional[condecimal(max_digits=5, decimal_places=2)]
    review_count: int
    current_market: Optional[condecimal(max_digits=10, decimal_places=2)]
    rarity_score: Optional[condecimal(max_digits=5, decimal_places=2)]
    qpr: Optional[condecimal(max_digits=5, decimal_places=2)]

    class Config:
        orm_mode = True


# --- CellarSlot schemas ------------------------------
class CellarSlotBase(BaseModel):
    rack: str
    row: str
    led_node_id: str

class CellarSlotCreate(CellarSlotBase):
    """Input for creating a slot."""
    pass

class CellarSlotRead(CellarSlotBase):
    """Response model for a slot."""
    id: UUID4

    class Config:
        orm_mode = True


# --- ScanEvent schemas --------------------------------
class ScanEventBase(BaseModel):
    wine_id: UUID4
    slot_id: UUID4
    event_type: EventTypeEnum
    timestamp: Optional[datetime] = None    # will default if not provided

class ScanEventCreate(ScanEventBase):
    """Input for logging a scan event."""
    pass

class ScanEventRead(ScanEventBase):
    """Response model for a scan, with nested relationships."""
    id: UUID4
    wine: WineRead
    slot: CellarSlotRead

    class Config:
        orm_mode = True