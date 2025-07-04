from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app import schemas, models
from app.database import get_db

router = APIRouter(prefix="/lookups", tags=["Lookups"])

@router.post(
    "/classifications",
    response_model=schemas.ClassificationRead,
    status_code=status.HTTP_201_CREATED
)
def create_classification(
    data: schemas.ClassificationCreate,
    db: Session = Depends(get_db)
):
    # optionally, verify if parent scope exists
    if data.country_id and not db.query(models.Country).get(data.country_id):
        raise HTTPException(status_code=400, detail= "Country does not exist")
    if data.region_id and not db.query(models.Region).get(data.region_id):
        raise HTTPException(status_code=400, detail= "Region does not exist")
    
    new = models.Classification(
        name=data.name,
        country_id=data.country_id,
        region_id=data.region_id
    )
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

@router.get(
    "/classifications",
    response_model=List[schemas.ClassificationRead]
)
def list_classifications(
    skip: int = 0,
    limit: int = 100,
    country_id: Optional[str] = None,
    region_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(models.Classification)
    if country_id:
        q = q.filter(models.Classification.country_id == country_id)
    if region_id:
        q = q.filter(models.Classification.region_id == region_id)
    return q.offset(skip).limit(limit).all()

@router.get(
    "/classifications/{id}",
    response_model=schemas.ClassificationRead
)
def get_classification(
    id: str,
    db: Session = Depends(get_db)
):
    cls = db.query(models.Classification).get(id)
    if not cls:
        raise HTTPException(status_code=404, detail= "Classification not found")
    return cls

@router.put(
    "/classifications/{id}",
    response_model=schemas.ClassificationRead
)
def update_classification(
    id: str,
    data: schemas.ClassificationCreate,
    db: Session = Depends(get_db)
):
    cls = db.query(models.Classification).get(id)
    if not cls:
        raise HTTPException(status_code=404, detail= "Classification not found")
    
    # optionally, revalidate scope
    cls.name = data.name
    cls.country_id = data.country_id
    cls.region_id = data.region_id
    db.commit()
    db.refresh(cls)
    return cls

@router.delete(
    "/classifications/{id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_classification(
    id: str,
    db: Session = Depends(get_db)
):
    cls = db.query(models.Classification).get(id)
    if not cls:
        raise HTTPException(status_code=404, detail= "Classification not found")
    
    db.delete(cls)
    db.commit()