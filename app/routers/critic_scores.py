from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/critic-scores", tags=["critic-scores"],)

# --- Create a critic score ---------------------------
@router.post(
    "",
    response_model = schemas.CriticScoreRead,
    status_code = status.HTTP_201_CREATED
)
def create_critic_score(
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
def list_critic_scores(
    wine_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    q = db.query(models.CriticScore)
    if wine_id:
        q = q.filter(models.CriticScore.wine_id == wine_id)
    return q.offset(skip)\
            .limit(limit)\
            .all()


# --- Get a single critic score by id ------------
@router.get(
    "/{critic_score_id}",
    response_model = schemas.CriticScoreRead
)
def get_critic_score(
    critic_score_id: str,
    db: Session = Depends(get_db)
):
    """
    Fetch a single critic score by its UUID
    """
    critic_score = db.query(models.CriticScore).get(critic_score_id)
    if not critic_score:
        raise HTTPException(status_code=404, detail= "Critic score not found")
    return critic_score

# --- Update an existing critic score --------------
@router.put(
    "/{critic_score_id}",
    response_model = schemas.CriticScoreRead
)
def update_critic_score(
    critic_score_id: str,
    data: schemas.CriticScoreCreate,
    db: Session = Depends(get_db)
):
    """
    Update an existing critic score's details
    """
    critic_score = db.query(models.CriticScore).get(critic_score_id)
    if not critic_score:
        raise HTTPException(status_code=404, detail= "Critic score not found")
    
    # Apply updates
    critic_score.wine_id       = data.wine_id
    critic_score.source        = data.source
    critic_score.score         = data.score
    critic_score.review_date   = data.review_date
    
    db.commit()
    db.refresh(critic_score)
    return critic_score

# --- Delete an existing critic score -----------------------
@router.delete(
    "/{critic_score_id}",
    status_code = status.HTTP_204_NO_CONTENT
)
def critic_score_delete(
    critic_score_id: str,
    db: Session = Depends(get_db)
):
    """
    Remove a critic score from inventory
    """
    critic_score = db.query(models.CriticScore).get(critic_score_id)
    if not critic_score:
        raise HTTPException(status_code=404, detail= "Critic score not found")
    db.delete(critic_score)
    db.commit()
    return None