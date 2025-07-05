from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get(
    "/{wine_id}",
    response_model = schemas.WineMetricsRead
)
def get_metrics(
    wine_id: str,
    db: Session = Depends(get_db)
):
    """
    Return the aggregated metrics record for a specific wine.
    """
    metrics = db.query(models.WineMetrics).get(wine_id)
    if not metrics:
        raise HTTPException(status_code=404, detail="Metrics not found for this wine")
    return metrics

# --- Update aggregate metrics automatically --------------------
@router.post(
    "/{wine_id}/recompute",
    response_model = schemas.WineMetricsRead,
    status_code = status.HTTP_200_OK
)
def recompute_metrics(
    wine_id: str,
    db: Session = Depends(get_db)
):
    """
    Recalculate and upsert the WineMetrics fora. given wine:
        - avg_score & review_count from CriticScore
        - (placeholders for current_market, rarity_score, qpr)
    """
    # 1. Ensure the wine exists
    wine = db.query(models.Wine).get(wine_id)
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    
    # 2. Gather all critic scores
    scores = db.query(models.CriticScore).filter(models.CriticScore.wine_id == wine_id).all()
    if not scores:
        raise HTTPException(status_code=404, detail="No critic scores to compute")
    
    count = len(scores)
    avg = sum([float(s.score) for s in scores]) / count    

    # 3. Upsert the WineMetrics row
    metrics = db.query(models.WineMetrics).get(wine_id)
    if not metrics:
        metrics = models.WineMetrics(wine_id=wine_id)
        db.add(metrics)

    metrics.avg_score    = round(avg,2)
    metrics.review_count = count
    # leave current_market, rarity_score, qpr as-is or null for now

    db.commit()
    db.refresh(metrics)
    return metrics