from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/scores", tags=["scores"],)

# --- Create a critic score ---------------------------
@router.post(
    "",
    response_model = schemas.CriticScoreRead,
    status_code = status.HTTP_201_CREATED
)
def create_score(
    data: schemas.CriticScoreCreate,
    db: Session = Depends(get_db)
):
    if not db.query(models.Wine).get(data.wine_id):
        raise HTTPException(status_code=400, detail= "Wine not found")
    new = models.CriticScore(**data.dict())
    
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

# --- List all critic scores --------------------------
@router.get(
    "",
    response_model = List[schemas.CriticScoreRead]
)
def list_scores(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return db.query(models.CriticScore)\
                .offset(skip)\
                .limit(limit)\
                .all()

# --- Get a single critic score by id ------------
@router.get(
    "/{score_id}",
    response_model = schemas.CriticScoreRead
)
def get_score(
    score_id: str,
    db: Session = Depends(get_db)
):
    """
    Fetch a single critic score by its UUID
    """
    score = db.query(models.CriticScore).get(score_id)
    if not score:
        raise HTTPException(status_code=404, detail= "Critic score not found")
    return score

# --- Update an existing critic score --------------
@router.put(
    "/{score_id}",
    response_model = schemas.CriticScoreRead
)
def update_score(
    score_id: str,
    data: schemas.CriticScoreCreate,
    db: Session = Depends(get_db)
):
    """
    Update an existing critic score's details
    """
    score = db.query(models.CriticScore).get(score_id)
    if not score:
        raise HTTPException(status_code=404, detail= "Critic score not found")
    
    # Apply updates
    score.wine_id       = data.wine_id
    score.source        = data.source
    score.score         = data.score
    score.review_date   = data.review_date
    
    db.commit()
    db.refresh(score)
    return score

# --- Delete an existing critic score -----------------------
@router.delete(
    "/{score_id}",
    status_code = status.HTTP_204_NO_CONTENT
)
def score_delete(
    score_id: str,
    db: Session = Depends(get_db)
):
    """
    Remove a critic score from inventory
    """
    score = db.query(models.CriticScore).get(score_id)
    if not score:
        raise HTTPException(status_code=404, detail= "Critic score not found")
    db.delete(score)
    db.commit()
    return None