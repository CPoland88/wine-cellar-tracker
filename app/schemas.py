from pydantic import BaseModel, UUID4
from typing import Optional, List

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