from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.city import City
from app.processing.aggregator import latest_air_quality, latest_weather
from app.schemas import CityOut, CityDetail

router = APIRouter(prefix="/cities", tags=["Cities"])


@router.get("/", response_model=list[CityOut], summary="List all tracked cities")
def list_cities(db: Session = Depends(get_db)):
    """Return all cities that AirPulse is currently tracking."""
    return db.query(City).order_by(City.name).all()


@router.get(
    "/{city_id}",
    response_model=CityDetail,
    summary="Get city details with latest readings",
)
def get_city(city_id: int, db: Session = Depends(get_db)):
    city = db.query(City).filter(City.id == city_id).first()
    if city is None:
        raise HTTPException(status_code=404, detail=f"City {city_id} not found")

    aq = latest_air_quality(db, city_id)
    w = latest_weather(db, city_id)

    return CityDetail(city=city, latest_air_quality=aq, latest_weather=w)
