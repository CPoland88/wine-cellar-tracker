from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import UUID4

from app import models, schemas
from app.database import get_db
from app.schemas import SlotColor
from app.models import ScanEvent, EventTypeEnum

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


# --- Search for bottles in the cellar ----------------
@router.post(
    "/search-bottle",
    response_model = List[SlotColor]
)
def search_bottle(
    wine_id: UUID4,
    db: Session = Depends(get_db)
):
    # 1. Find the current slot for this bottle by taking its latest
    #    event (IN or OUT)
    latest = (
        db.query(ScanEvent)
            .filter(ScanEvent.wine_id == wine_id)
            .order_by(ScanEvent.timestamp.desc())
            .first()
    )

    # 2. If there were *no* events at all, that's an error
    if latest is None:
        raise HTTPException(status_code=404, detail="Wine has never been slotted in or out")
    
    # 3. If the last event was an OUT, return inventory error
    if latest.event_type == EventTypeEnum.OUT:
        raise HTTPException(status_code=400, detail="Wine is currently out of the cellar")
    else:
        highlight_id = latest.slot_id

    # 4. Build the color map
    slots = db.query(models.CellarSlot).all()
    return [
        schemas.SlotColor(
            slot_id = slot.id,
            color = "green" if slot.id == highlight_id else "red"
        )
        for slot in slots
    ]    

@router.post(
    "/search-lookup",
    response_model = List[SlotColor]
)
def search_lookup(
    country_id: Optional[UUID4] = None,
    region_id: Optional[UUID4] = None,
    subregion_id: Optional[UUID4] = None,
    varietal_id: Optional[UUID4] = None,
    db: Session = Depends(get_db)
):
    # 1. Find all wines matchimg any of the given filters
    q = db.query(models.Wine.id)
    if country_id:
        q = q.filter(models.Wine.country_id == country_id)
    if region_id:
        q = q.filter(models.Wine.region_id == region_id)
    if subregion_id:
        q = q.filter(models.Wine.subregion_id == subregion_id)
    if varietal_id:
        q = q.join(models.Wine.varietals).filter(models.wine_varietals.c.varietal_id == varietal_id)

    wine_ids = [w[0] for w in q.all()]

    # 2. For each of those wines, find its current slot via latest IN event
    in_events = (
        db.query(ScanEvent.wine_id, ScanEvent.slot_id, func.max(ScanEvent.timestamp).label("ts"))
            .filter(ScanEvent.wine_id.in_(wine_ids), ScanEvent.event_type == EventTypeEnum.IN)
            .group_by(ScanEvent.wine_id, ScanEvent.slot_id)
    )
    matched_slots = {row.slot_id for row in in_events}

    slots = db.query(models.CellarSlot).all()
    return [
        SlotColor(
            slot_id = slot.id,
            color = "green" if slot.id in matched_slots else "red"
        )
        for slot in slots
    ]


# --- Scan a bottle in and slot it accordingly -----------------------------
@router.post(
    "/scan-in",
    response_model = List[SlotColor]
)
def scan_in_suggestions(
    wine_id: UUID4,
    db: Session = Depends(get_db)
):
    # 1. Compute occupied slots: latest even per slot - if it's IN, it's filled
    subq = (
        db.query(ScanEvent.slot_id, func.max(ScanEvent.timestamp).label("ts"))
        .group_by(ScanEvent.slot_id)
        .subquery()
    )
    latest = db.query(ScanEvent).join(
        subq,
        (ScanEvent.slot_id == subq.c.slot_id) &
        (ScanEvent.timestamp == subq.c.ts)
    )
    occupied = {e.slot_id for e in latest if e.event_type == EventTypeEnum.IN}

    # 2. Free slots are those not occupied
    free_slots = db.query(models.CellarSlot).filter(~models.CellarSlot.id.in_(occupied)).all()

    return [
        SlotColor(slot_id = slot.id, color = "blue")
        for slot in free_slots
    ]

@router.post(
    "/slot-in",
    response_model = schemas.ScanEventRead,
    status_code = status.HTTP_201_CREATED
)
def slot_in_wine(
    wine_id: UUID4,
    slot_id: UUID4,
    db: Session = Depends(get_db)
):
    # 1. Validate wine exists
    wine = db.query(models.Wine).get(wine_id)
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    slot = db.query(models.CellarSlot).get(slot_id)

    # 2. Valide slot exists and is free
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    last = (
        db.query(ScanEvent)
            .filter(ScanEvent.slot_id == slot_id)
            .order_by(ScanEvent.timestamp.desc())
            .first()
    )
    if last and last.event_type == EventTypeEnum.IN:
        raise HTTPException(status_code=400, detail="Slot is occupied")
    
    # 3. Create IN event
    ev = models.ScanEvent(
        wine_id=wine_id, 
        slot_id=slot_id,
        event_type = EventTypeEnum.IN
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)

    # 4. Stub LED: for now, just log
    print(f"[LED STUB] slot {slot_id} -> blue")

    return ev


# --- Scan a wine out and open up the slot ------------------
@router.post(
    "/slot-out",
    response_model = schemas.ScanEventRead,
    status_code = status.HTTP_201_CREATED
)
def slot_out_wine(
    wine_id: UUID4,
    db: Session = Depends(get_db)
):
    # 1. Validate wine exists
    wine = db.query(models.Wine).get(wine_id)
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    
    # 2. Find the slot it's currently in
    last_in = (
        db.query(ScanEvent)
            .filter(
                ScanEvent.wine_id == wine_id,
                ScanEvent.event_type == EventTypeEnum.IN
            )
            .order_by(ScanEvent.timestamp.desc())
            .first()
    )
    if not last_in:
        raise HTTPException(status_code=400, detail="Wine is not in any slot")
    
    # 3. Ensure it hasn't already been taken out
    last_out = (
        db.query(ScanEvent)
            .filter(
                ScanEvent.wine_id == wine_id,
                ScanEvent.event_type == EventTypeEnum.OUT
            )
            .order_by(ScanEvent.timestamp.desc())
            .first()
    )
    if last_out and last_out.timestamp > last_in.timestamp:
        raise HTTPException(status_code=400, detail="Wine is already out")
    
    # 4. Create OUT event
    ev = models.ScanEvent(
        wine_id = wine_id,
        slot_id = last_in.slot_id,
        event_type = EventTypeEnum.OUT
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)

    # 5. Stub LED: mark that slot red (just a console log)
    print(f"[LED STUB] slot {last_in.slot_id} -> red")

    return ev