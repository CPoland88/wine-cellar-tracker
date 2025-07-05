from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/scan-events",tags=["scan-events"],)


# --- Create a scan event --------------------------------------
@router.post(
    "",
    response_model = schemas.ScanEventRead,
    status_code = status.HTTP_201_CREATED
)
def create_scan_event(
    data: schemas.ScanEventCreate,
    db: Session = Depends(get_db)
):
    # validate foreign keys
    if not db.query(models.Wine).get(data.wine_id):
        raise HTTPException(status_code=400, detail="Wine not found")
    if not db.query(models.CellarSlot).get(data.slot_id):
        raise HTTPException(status_code=400, detail="Slot not found")
    
    new = models.ScanEvent(**data.dict())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

# --- List scan events -------------------------------------------
@router.get(
    "",
    response_model = List[schemas.ScanEventRead]
)
def list_scan_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return db.query(models.ScanEvent)\
                .offset(skip)\
                .limit(limit)\
                .all()

# --- Get scan event by ID ----------------------------------------
@router.get(
    "/{event_id}",
    response_model = schemas.ScanEventRead
)
def get_scan_event(
    event_id: str,
    db: Session = Depends(get_db)
):
    event = db.query(models.ScanEvent).get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Scan event not found")
    return event

# --- Update a scan event ----------------------------------------
@router.put(
    "/{event_id}",
    response_model = schemas.ScanEventRead
)
def update_scan_event(
    event_id: str,
    data: schemas.ScanEventCreate,
    db: Session = Depends(get_db)
):
    event = db.query(models.ScanEvent).get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Scan event not found")
    
    event.wine_id       = data.wine_id
    event.slot_id       = data.slot_id
    event.event_type    = data.event_type
    event.timestamp     = data.timestamp

    db.commit()
    db.refresh(event)
    return event

# --- Delete a scan event ----------------------------------------
@router.delete(
    "/{event_id}",
    status_code = status.HTTP_204_NO_CONTENT
)
def delete_scan_event(
    event_id: str,
    db: Session = Depends(get_db)
):
    event = db.query(models.ScanEvent).get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Scan event not found")
    
    db.delete(event)
    db.commit()
    return None