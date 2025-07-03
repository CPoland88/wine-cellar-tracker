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