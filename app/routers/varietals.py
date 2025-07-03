from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/lookups", tags=["Lookups"])

@router.post(
    "/varietals",
    response_model=schemas.VarietalRead,
    status_code=status.HTTP_201_CREATED
)
def create_varietal(
    data: schemas.VarietalCreate,
    db: Session = Depends(get_db)
):
    # 1. Prevent duplicates
    existing = db.query(models.Varietal).filter(models.Varietal.name == data.name).first()
    if existing:
        raise HTTPException(400, "Varietal already exists")
    
    # 2. Create & return
    new = models.Varietal(name=data.name)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

# --- Get a list of all varietals ------------------------
@router.get(
    "/varietals",
    response_model=List[schemas.VarietalRead]
)
def list_varietals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return db.query(models.Varietal)\
                .offset(skip)\
                .limit(limit)\
                .all()

# --- Get a single Varietal by ID --------------------------
@router.get(
    "/varietals/{varietal_id}",
    response_model=schemas.VarietalRead
)
def get_varietal(
    varietal_id: str,
    db: Session = Depends(get_db)
):
    varietal = db.query(models.Varietal).get(varietal_id)
    if not varietal:
        raise HTTPException(404, "Varietal not found")
    return varietal

# --- Update an existing Varietal ---------------------------
@router.put(
    "/varietals/{varietal_id}",
    response_model=schemas.VarietalRead
)
def update_varietal(
    varietal_id: str,
    data: schemas.VarietalCreate,
    db: Session = Depends(get_db)
):
    varietal = db.query(models.Varietal).get(varietal_id)
    if not varietal:
        raise HTTPException(404, "Varietal not found")
    varietal.name = data.name
    db.commit()
    db.refresh(varietal)
    return varietal

# --- Delete a varietal --------------------------------------
@router.delete(
    "/varietals/{varietal_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_varietal(
    varietal_id: str,
    db: Session = Depends(get_db)
):
    varietal = db.query(models.Varietal).get(varietal_id)
    if not varietal:
        raise HTTPException(404, "Varietal not found")
    db.delete(varietal)
    db.commit()
    return None