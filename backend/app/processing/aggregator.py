from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.air_quality import AirQualityReading
from app.models.weather import WeatherReading


def avg_aqi_last_n_hours(db: Session, city_id: int, hours: int = 24) -> Optional[float]:
    since = datetime.now(tz=timezone.utc) - timedelta(hours=hours)
    result = (
        db.query(func.avg(AirQualityReading.aqi))
        .filter(
            AirQualityReading.city_id == city_id,
            AirQualityReading.recorded_at >= since,
            AirQualityReading.aqi.isnot(None),
        )
        .scalar()
    )
    return round(float(result), 1) if result is not None else None


def avg_weather_last_n_hours(
    db: Session, city_id: int, hours: int = 24
) -> dict:
    since = datetime.now(tz=timezone.utc) - timedelta(hours=hours)
    row = (
        db.query(
            func.avg(WeatherReading.temperature).label("temperature"),
            func.avg(WeatherReading.humidity).label("humidity"),
            func.avg(WeatherReading.wind_speed).label("wind_speed"),
            func.avg(WeatherReading.pressure).label("pressure"),
        )
        .filter(
            WeatherReading.city_id == city_id,
            WeatherReading.recorded_at >= since,
        )
        .first()
    )

    def _round(val) -> Optional[float]:
        return round(float(val), 2) if val is not None else None

    return {
        "temperature": _round(row.temperature),
        "humidity": _round(row.humidity),
        "wind_speed": _round(row.wind_speed),
        "pressure": _round(row.pressure),
    }


def latest_air_quality(db: Session, city_id: int) -> Optional[AirQualityReading]:
    return (
        db.query(AirQualityReading)
        .filter(AirQualityReading.city_id == city_id)
        .order_by(AirQualityReading.recorded_at.desc())
        .first()
    )


def latest_weather(db: Session, city_id: int) -> Optional[WeatherReading]:
    return (
        db.query(WeatherReading)
        .filter(WeatherReading.city_id == city_id)
        .order_by(WeatherReading.recorded_at.desc())
        .first()
    )
