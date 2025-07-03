from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import schemas, models
from app.database import get_db

router = APIRouter(prefix="/lookups", tags=["Lookups"])

# --- Country Endpoints ----------------------------
@router.post(
    "/countries",
    response_model=schemas.CountryRead,
    status_code=status.HTTP_201_CREATED
)
def create_country(
    country: schemas.CountryCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(models.Country)\
                .filter(models.Country.name == country.name)\
                .first()
    if existing:
        raise HTTPException(400, "Country already exists")

    new = models.Country(name=country.name)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

@router.get(
    "/countries",
    response_model=List[schemas.CountryRead]
)
def list_countries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return db.query(models.Country)\
            .offset(skip)\
            .limit(limit)\
            .all()

@router.get(
    "/countries/{country_id}",
    response_model=schemas.CountryRead
)
def get_country(
    country_id: str,
    db: Session = Depends(get_db)
):
    country = db.query(models.Country).get(country_id)
    if not country:
        raise HTTPException(404, "Country not found")
    return country

@router.put(
    "countries/{country_id}",
    response_model=schemas.CountryRead
)
def update_country(
    country_id: str,
    country_in: schemas.CountryCreate,
    db: Session = Depends(get_db)
):
    country = db.query(models.Country).get(country_id)
    if not country:
        raise HTTPException(404, "Country not found")
    country.name = country_in.name
    db.commit()
    db.refresh(country)
    return country

@router.delete(
    "/countries/{country_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_country(
    country_id: str,
    db: Session = Depends(get_db)
):
    country = db.query(models.Country).get(country_id)
    if not country:
        raise HTTPException(404, "Country not found")
    db.delete(country)
    db.commit()


# --- Region Endpoints ----------------------------
@router.post(
    "/regions",
    response_model=schemas.RegionRead,
    status_code=status.HTTP_201_CREATED
)
def create_region(
    region: schemas.RegionCreate,
    db: Session = Depends(get_db)
):
    # 1. Ensure the parent country exists
    country = db.query(models.Country).get(region.country_id)
    if not country:
        raise HTTPException(404, "Country does not exist")
    
    # 2. Prevent duplicate region names within the same country
    existing = db.query(models.Region)\
                .filter(
                    models.Region.name == region.name,
                    models.Region.country_id == region.country_id
                )\
                .first()
    if existing:
        raise HTTPException(400, "Region already exists for this country")

    # 3. Create, commit and return the new region
    new = models.Region(
        name=region.name,
        country_id=region.country_id
    )
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

@router.get(
    "/regions",
    response_model=List[schemas.RegionRead]
)
def list_regions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return db.query(models.Region)\
            .offset(skip)\
            .limit(limit)\
            .all()

@router.get(
    "/regions/{region_id}",
    response_model=schemas.RegionRead
)
def get_region(
    region_id: str,
    db: Session = Depends(get_db)
):
    region = db.query(models.Region).get(region_id)
    if not region:
        raise HTTPException(404, "Region not found")
    return region

@router.put(
    "/regions/{region_id}",
    response_model=schemas.RegionRead
)
def update_region(
    region_id: str,
    region_in: schemas.RegionCreate,
    db: Session = Depends(get_db)
):
    region = db.query(models.Region).get(region_id)
    if not region:
        raise HTTPException(404, "Region not found")
    
    # Ensure the parent country exists
    if not db.query(models.Country).get(region_in.country_id):
        raise HTTPException(404, "Country does not exist")
    
    region.name = region_in.name
    region.country_id = region_in.country_id
    db.commit()
    db.refresh(region)
    return region

@router.delete(
    "/regions/{region_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_region(
    region_id: str,
    db: Session = Depends(get_db)
):
    region = db.query(models.Region).get(region_id)
    if not region:
        raise HTTPException(404, "Region not found")
    db.delete(region)
    db.commit()

# --- Subregion Endpoints ---------------------------
@router.post(
    "/subregions",
    response_model=schemas.SubregionRead,
    status_code=status.HTTP_201_CREATED
)
def create_subregion(
    subregion: schemas.SubregionCreate,
    db: Session = Depends(get_db)
):
    # 1. Ensure the parent region exists
    region = db.query(models.Region).get(subregion.region_id)
    if not region:
        raise HTTPException(404, "Region does not exist")
    
    # 2. Prevent duplicate subregion names within the same region
    existing = db.query(models.Subregion)\
                .filter(
                    models.Subregion.name == subregion.name,
                    models.Subregion.region_id == subregion.region_id
                )\
                .first()
    
    if existing:
        raise HTTPException(400, "Subregion already exists for this region")

    # 3. Create, commit and return the new subregion
    new = models.Subregion(
        name=subregion.name,
        region_id=subregion.region_id
    )
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

@router.get(
    "/subregions",
    response_model=List[schemas.SubregionRead]
)
def list_subregions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return db.query(models.Subregion)\
            .offset(skip)\
            .limit(limit)\
            .all()

@router.get(
    "/subregions/{subregion_id}",
    response_model=schemas.SubregionRead
)
def get_subregion(
    subregion_id: str,
    db: Session = Depends(get_db)
):
    subregion = db.query(models.Subregion).get(subregion_id)
    if not subregion:
        raise HTTPException(404, "Subregion not found")
    return subregion

@router.put(
    "/subregions/{subregion_id}",
    response_model=schemas.SubregionRead
)
def update_subregion(
    subregion_id: str,
    subregion_in: schemas.SubregionCreate,
    db: Session = Depends(get_db)
):
    subregion = db.query(models.Subregion).get(subregion_id)
    if not subregion:
        raise HTTPException(404, "Subregion not found")
    
    # Ensure the parent region exists
    if not db.query(models.Region).get(subregion_in.region_id):
        raise HTTPException(404, "Region does not exist")
    
    subregion.name = subregion_in.name
    subregion.region_id = subregion_in.region_id
    db.commit()
    db.refresh(subregion)
    return subregion

@router.delete(
    "/subregions/{subregion_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_subregion(
    subregion_id: str,
    db: Session = Depends(get_db)
):
    subregion = db.query(models.Subregion).get(subregion_id)
    if not subregion:
        raise HTTPException(404, "Subregion not found")
    db.delete(subregion)
    db.commit()