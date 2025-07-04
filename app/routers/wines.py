from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix = '/wines', tags = ['wines'])

@router.post(
    "",
    response_model = schemas.WineRead,
    status_code = status.HTTP_201_CREATED
)
def create_wine(
    data: schemas.WineCreate,
    db: Session = Depends(get_db)
):
    # 1. Validate required lookups exist
    if not db.query(models.Country).get(data.country_id):
        raise HTTPException(status_code=400, detail= "Country not found")
    if not db.query(models.Region).get(data.region_id):
        raise HTTPException(status_code=400, detail= "Region not found")
    if data.subregion_id and not db.query(models.Subregion).get(data.subregion_id):
        raise HTTPException(status_code=400, detail= "Subregion not found")
    if data.classification_id and not db.query(models.Classification).get(data.classification_id):
        raise HTTPException(status_code=400, detail= "Classification not found")
    
    # 2. Create the wine record
    new = models.Wine(
        producer = data.producer,
        label = data.label,
        vintage = data.vintage,
        country_id = data.country_id,
        region_id = data.region_id,
        subregion_id = data.subregion_id,
        classification_id = data.classification_id,
        bottle_size = data.bottle_size,
        closure_type = data.closure_type,
        abv = data.abv,
    )

    db.add(new)
    db.commit()
    db.refresh(new)
    return new

# --- Get a list of all wines -----------------
@router.get(
    "",
    response_model = List[schemas.WineRead]
)
def list_wines(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Return a paginated list of all wines
    """
    return db.query(models.Wine)\
                .offset(skip)\
                .limit(limit)\
                .all()

# --- Get a single wine by id ------------
@router.get(
    "/{wine_id}",
    response_model = schemas.WineRead
)
def get_wine(
    wine_id = str,
    db: Session = Depends(get_db)
):
    """
    Fetch a single wine by its UUID
    """
    wine = db.query(models.Wine).get(wine_id)
    if not wine:
        raise HTTPException(status_code=404, detail= "Wine not found")
    return wine

# --- Update an existing wine --------------
@router.put(
    "/{wine_id}",
    response_model = schemas.WineRead
)
def update_wine(
    wine_id: str,
    data: schemas.WineCreate,
    db: Session = Depends(get_db)
):
    """
    Update an existing wine's details
    """
    wine = db.query(models.Wine).get(wine_id)
    if not wine:
        raise HTTPException(status_code=404, detail= "Wine not found")
    
    # Validate lookups
    if not db.query(models.Country).get(data.country_id):
        raise HTTPException(status_code=400, detail= "Country not found")
    if not db.query(models.Region).get(data.region_id):
        raise HTTPException(status_code=400, detail= "Region not found")
    if data.subregion_id and not db.query(models.Subregion).get(data.subregion_id):
        raise HTTPException(status_code=400, detail= "Subregion not found")
    if data.classification_id and not db.query(models.Classification).get(data.classification_id):
        raise HTTPException(status_code=400, detail= "Classification not found")
    
    # Apply updates
    wine.producer           = data.producer
    wine.label              = data.label
    wine.vintage            = data.vintage
    wine.country_id         = data.country_id
    wine.region_id          = data.region_id
    wine.subregion_id       = data.region_id
    wine.classification_id  = data.classification_id
    wine.bottle_size        = data.bottle_size
    wine.closure_type       = data.closure_type
    wine.abv                = data.abv

    db.commit()
    db.refresh(wine)
    return wine

# --- Delete an existing wine -----------------------
@router.delete(
    "/{wine_id}",
    status_code = status.HTTP_204_NO_CONTENT
)
def wine_delete(
    wine_id: str,
    db: Session = Depends(get_db)
):
    """
    Remove a wine from inventory
    """
    wine = db.query(models.Wine).get(wine_id)
    if not wine:
        raise HTTPException(status_code=404, detail= "Wine not found")
    db.delete(wine)
    db.commit()
    return None