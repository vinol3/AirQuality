from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.city import City
from app.models.air_quality import AirQualityReading
from app.schemas import AirQualityOut

router = APIRouter(prefix="/cities", tags=["Air Quality"])


@router.get(
    "/{city_id}/air-quality",
    response_model=list[AirQualityOut],
    summary="Get air quality readings for a city",
)
def get_air_quality(
    city_id: int,
    hours: int = Query(default=48, ge=1, le=720, description="Look-back window in hours"),
    db: Session = Depends(get_db),
):
    city = db.query(City).filter(City.id == city_id).first()
    if city is None:
        raise HTTPException(status_code=404, detail=f"City {city_id} not found")

    since = datetime.now(tz=timezone.utc) - timedelta(hours=hours)
    readings = (
        db.query(AirQualityReading)
        .filter(
            AirQualityReading.city_id == city_id,
            AirQualityReading.recorded_at >= since,
        )
        .order_by(AirQualityReading.recorded_at.asc())
        .all()
    )
    return readings
