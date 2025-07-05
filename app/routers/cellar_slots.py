from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/cellar-slots", tags=["cellar-slots"],)

# --- Create a slot -------------------------------------
@router.post(
    "",
    response_model = schemas.CellarSlotRead,
    status_code = status.HTTP_201_CREATED
)
def create_slot(
    data: schemas.CellarSlotCreate,
    db: Session = Depends(get_db)
):
    # prevent duplicates
    exists = (
        db.query(models.CellarSlot)\
            .filter_by(rack=data.rack, row=data.row)\
            .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="Slot already exists")
    
    new = models.CellarSlot(**data.dict())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

# --- List slots ----------------------------------------
@router.get(
    "",
    response_model = List[schemas.CellarSlotRead]
)
def list_slots(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return db.query(models.CellarSlot)\
                .offset(skip)\
                .limit(limit)\
                .all()


# --- Get slot by ID ------------------------------------
@router.get(
    "/{slot_id}",
    response_model = schemas.CellarSlotRead
)
def get_slot(
    slot_id: str,
    db: Session = Depends(get_db)
):
    slot = db.query(models.CellarSlot).get(slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    return slot


# --- Update a slot --------------------------------------
@router.put(
    "/{slot_id}",
    response_model = schemas.CellarSlotRead
)
def update_slot(
    slot_id: str,
    data: schemas.CellarSlotCreate,
    db: Session = Depends(get_db)
):
    slot = db.query(models.CellarSlot).get(slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    slot.rack           = data.rack
    slot.row            = data.row
    slot.led_node_id    = data.led_node_id

    db.commit()
    db.refresh(slot)
    return slot


# --- Delete a slot ----------------------------------
@router.delete(
    "/{slot_id}",
    status_code = status.HTTP_204_NO_CONTENT
)
def delete_slot(
    slot_id: str,
    db: Session = Depends(get_db)
):
    slot = db.query(models.CellarSlot).get(slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    db.delete(slot)
    db.commit()
    return None