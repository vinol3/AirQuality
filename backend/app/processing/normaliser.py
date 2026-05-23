"""
Data Normalisation Layer
=========================
Converts raw API responses into validated ORM model instances.
Responsibility: type coercion, null handling, range validation.
"""
import structlog
from datetime import datetime, timezone
from typing import Optional
from app.models.air_quality import AirQualityReading
from app.models.weather import WeatherReading

log = structlog.get_logger()

AQI_MIN, AQI_MAX = 0, 500
PM_MIN, PM_MAX = 0.0, 1000.0
TEMP_MIN, TEMP_MAX = -60.0, 60.0
HUMIDITY_MIN, HUMIDITY_MAX = 0, 100
WIND_MIN, WIND_MAX = 0.0, 100.0
PRESSURE_MIN, PRESSURE_MAX = 800, 1100


def normalise_air_quality(
    city_id: int,
    raw: dict,
    recorded_at: Optional[datetime] = None,
) -> Optional[AirQualityReading]:
    if recorded_at is None:
        recorded_at = datetime.now(tz=timezone.utc)

    aqi = _clamp_int(raw.get("aqi"), AQI_MIN, AQI_MAX, "aqi", city_id)
    pm25 = _clamp_float(raw.get("pm25"), PM_MIN, PM_MAX, "pm25", city_id)
    pm10 = _clamp_float(raw.get("pm10"), PM_MIN, PM_MAX, "pm10", city_id)

    if aqi is None:
        log.warning("normalise_skip_aq", city_id=city_id, reason="aqi is None")
        return None

    return AirQualityReading(
        city_id=city_id,
        recorded_at=recorded_at,
        aqi=aqi,
        pm25=pm25,
        pm10=pm10,
        source="iqair",
    )


def normalise_weather(
    city_id: int,
    raw: dict,
    recorded_at: Optional[datetime] = None,
) -> Optional[WeatherReading]:
    if recorded_at is None:
        recorded_at = datetime.now(tz=timezone.utc)

    temperature = _clamp_float(raw.get("temperature"), TEMP_MIN, TEMP_MAX, "temperature", city_id)
    humidity = _clamp_int(raw.get("humidity"), HUMIDITY_MIN, HUMIDITY_MAX, "humidity", city_id)
    wind_speed = _clamp_float(raw.get("wind_speed"), WIND_MIN, WIND_MAX, "wind_speed", city_id)
    pressure = _clamp_int(raw.get("pressure"), PRESSURE_MIN, PRESSURE_MAX, "pressure", city_id)
    description = str(raw.get("description", ""))[:100] if raw.get("description") else None

    if temperature is None:
        log.warning("normalise_skip_weather", city_id=city_id, reason="temperature is None")
        return None

    return WeatherReading(
        city_id=city_id,
        recorded_at=recorded_at,
        temperature=temperature,
        humidity=humidity,
        wind_speed=wind_speed,
        pressure=pressure,
        description=description,
        source="openweathermap",
    )


def aqi_to_category(aqi: Optional[int]) -> str:
    if aqi is None:
        return "Unknown"
    if aqi <= 50:
        return "Good"
    if aqi <= 100:
        return "Moderate"
    if aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    if aqi <= 200:
        return "Unhealthy"
    if aqi <= 300:
        return "Very Unhealthy"
    return "Hazardous"


def aqi_to_color(aqi: Optional[int]) -> str:
    if aqi is None:
        return "#9e9e9e"
    if aqi <= 50:
        return "#4caf50"
    if aqi <= 100:
        return "#ffeb3b"
    if aqi <= 150:
        return "#ff9800"
    if aqi <= 200:
        return "#f44336"
    if aqi <= 300:
        return "#9c27b0"
    return "#7b1fa2"


def _clamp_int(
    value, lo: int, hi: int, field: str, city_id: int
) -> Optional[int]:
    if value is None:
        return None
    try:
        v = int(value)
    except (TypeError, ValueError):
        log.warning("field_type_error", city_id=city_id, field=field, value=value)
        return None
    if not (lo <= v <= hi):
        log.warning("field_out_of_range", city_id=city_id, field=field, value=v, lo=lo, hi=hi)
        return None
    return v


def _clamp_float(
    value, lo: float, hi: float, field: str, city_id: int
) -> Optional[float]:
    if value is None:
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        log.warning("field_type_error", city_id=city_id, field=field, value=value)
        return None
    if not (lo <= v <= hi):
        log.warning("field_out_of_range", city_id=city_id, field=field, value=v, lo=lo, hi=hi)
        return None
    return round(v, 2)
