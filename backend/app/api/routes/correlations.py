from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.city import City
from app.processing.correlations import city_correlations
from app.schemas import CorrelationResult

router = APIRouter(prefix="/cities", tags=["Correlations"])


@router.get(
    "/{city_id}/correlation",
    response_model=CorrelationResult,
    summary="AQI ↔ weather correlation for a city",
)
def get_correlation(
    city_id: int,
    days: int = Query(default=30, ge=7, le=365, description="Look-back window in days"),
    db: Session = Depends(get_db),
):
    city = db.query(City).filter(City.id == city_id).first()
    if city is None:
        raise HTTPException(status_code=404, detail=f"City {city_id} not found")

    corr = city_correlations(db, city_id, days=days)
    return CorrelationResult(city=city, **corr)
