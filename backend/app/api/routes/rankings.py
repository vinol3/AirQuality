from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.city import City
from app.processing.aggregator import latest_air_quality, avg_aqi_last_n_hours
from app.processing.normaliser import aqi_to_category, aqi_to_color
from app.schemas import CityRanking

router = APIRouter(prefix="/rankings", tags=["Rankings"])


@router.get(
    "/",
    response_model=list[CityRanking],
    summary="City rankings by current AQI",
)
def get_rankings(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    cities = db.query(City).all()

    rankings = []
    for city in cities:
        latest = latest_air_quality(db, city.id)
        latest_aqi = latest.aqi if latest else None
        avg_24h = avg_aqi_last_n_hours(db, city.id, hours=24)

        rankings.append(
            {
                "city": city,
                "latest_aqi": latest_aqi,
                "avg_aqi_24h": avg_24h,
                "aqi_category": aqi_to_category(latest_aqi),
                "aqi_color": aqi_to_color(latest_aqi),
            }
        )

    rankings.sort(
        key=lambda r: (r["latest_aqi"] is None, r["latest_aqi"] or 9999)
    )

    result = []
    for i, r in enumerate(rankings[:limit], start=1):
        result.append(CityRanking(rank=i, **r))

    return result
