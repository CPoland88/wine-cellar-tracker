from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/purchases", tags=["purchases"],)

# --- Create a purchase ---------------------------
@router.post(
    "",
    response_model = schemas.PurchaseRead,
    status_code = status.HTTP_201_CREATED
)
def create_purchase(
    data: schemas.PurchaseCreate,
    db: Session = Depends(get_db)
):
    if not db.query(models.Wine).get(data.wine_id):
        raise HTTPException(status_code=400, detail= "Wine not found")
    new = models.Purchase(**data.dict())
    
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

# --- List all purchases --------------------------
@router.get(
    "",
    response_model = List[schemas.PurchaseRead]
)
def list_purchases(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return db.query(models.Purchase)\
                .offset(skip)\
                .limit(limit)\
                .all()

# --- Get a single purchase by id ------------
@router.get(
    "/{purchase_id}",
    response_model = schemas.PurchaseRead
)
def get_purchase(
    purchase_id = str,
    db: Session = Depends(get_db)
):
    """
    Fetch a single purchase by its UUID
    """
    purchase = db.query(models.Purchase).get(purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail= "Purchase not found")
    return purchase

# --- Update an existing Purchase --------------
@router.put(
    "/{purchase_id}",
    response_model = schemas.PurchaseRead
)
def update_purchase(
    purchase_id: str,
    data: schemas.PurchaseCreate,
    db: Session = Depends(get_db)
):
    """
    Update an existing purchase's details
    """
    purchase = db.query(models.Purchase).get(purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail= "Purchase not found")
    
    # Apply updates
    purchase.wine_id        = data.wine_id
    purchase.purchase_date  = data.purchase_date
    purchase.price_amount   = data.price_amount
    purchase.price_currency = data.price_currency
    purchase.receipt_url    = data.receipt_url

    db.commit()
    db.refresh(purchase)
    return purchase

# --- Delete an existing purchase -----------------------
@router.delete(
    "/{purchase_id}",
    status_code = status.HTTP_204_NO_CONTENT
)
def purchase_delete(
    purchase_id: str,
    db: Session = Depends(get_db)
):
    """
    Remove a purchase from inventory
    """
    purchase = db.query(models.Purchase).get(purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail= "Purchase not found")
    db.delete(purchase)
    db.commit()
    return None