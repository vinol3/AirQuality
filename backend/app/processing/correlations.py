import math
from typing import Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.air_quality import AirQualityReading
from app.models.weather import WeatherReading
from sqlalchemy import func, case


def pearson(x: list[float], y: list[float]) -> Optional[float]:
    n = len(x)
    if n < 3:
        return None

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    denom_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x))
    denom_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y))

    if denom_x == 0 or denom_y == 0:
        return None

    r = numerator / (denom_x * denom_y)
    return round(max(-1.0, min(1.0, r)), 4)


def city_correlations(db: Session, city_id: int, days: int = 30) -> dict:
    
    since = datetime.now(tz=timezone.utc) - timedelta(days=days)

    aq_rows = (
        db.query(AirQualityReading)
        .filter(
            AirQualityReading.city_id == city_id,
            AirQualityReading.recorded_at >= since,
            AirQualityReading.aqi.isnot(None),
        )
        .order_by(AirQualityReading.recorded_at)
        .all()
    )

    if not aq_rows:
        return {
            "temperature_correlation": None,
            "humidity_correlation": None,
            "wind_speed_correlation": None,
            "pressure_correlation": None,
            "data_points": 0,
        }

    aqi_vals, temps, humids, winds, pressures = [], [], [], [], []
    tolerance = timedelta(minutes=30)

    for aq in aq_rows:
        w = (
            db.query(WeatherReading)
            .filter(
                WeatherReading.city_id == city_id,
                WeatherReading.recorded_at >= aq.recorded_at - tolerance,
                WeatherReading.recorded_at <= aq.recorded_at + tolerance,
            )
            .order_by(
                func_abs_diff(WeatherReading.recorded_at, aq.recorded_at)
            )
            .first()
        )
        if w is None:
            continue

        aqi_vals.append(float(aq.aqi))
        temps.append(float(w.temperature) if w.temperature is not None else None)
        humids.append(float(w.humidity) if w.humidity is not None else None)
        winds.append(float(w.wind_speed) if w.wind_speed is not None else None)
        pressures.append(float(w.pressure) if w.pressure is not None else None)

    n = len(aqi_vals)

    def _corr(metric_vals: list) -> Optional[float]:
        pairs = [(a, m) for a, m in zip(aqi_vals, metric_vals) if m is not None]
        if len(pairs) < 3:
            return None
        return pearson([p[0] for p in pairs], [p[1] for p in pairs])

    return {
        "temperature_correlation": _corr(temps),
        "humidity_correlation": _corr(humids),
        "wind_speed_correlation": _corr(winds),
        "pressure_correlation": _corr(pressures),
        "data_points": n,
    }


def func_abs_diff(col, val):
    diff = col - val
    return case((diff >= timedelta(0), diff), else_=-diff)
