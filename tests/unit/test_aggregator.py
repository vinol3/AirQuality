from datetime import datetime, timedelta, timezone
import pytest
from app.processing.aggregator import (
    avg_aqi_last_n_hours,
    latest_air_quality,
    latest_weather,
)
from app.models.air_quality import AirQualityReading
from app.models.weather import WeatherReading


def _make_aq(city_id: int, aqi: int, hours_ago: float = 1.0):
    return AirQualityReading(
        city_id=city_id,
        aqi=aqi,
        pm25=aqi * 0.35,
        pm10=aqi * 0.55,
        recorded_at=datetime.now(tz=timezone.utc) - timedelta(hours=hours_ago),
        source="iqair",
    )


def _make_weather(city_id: int, temp: float, hours_ago: float = 1.0):
    return WeatherReading(
        city_id=city_id,
        temperature=temp,
        humidity=65,
        wind_speed=4.0,
        pressure=1013,
        recorded_at=datetime.now(tz=timezone.utc) - timedelta(hours=hours_ago),
        source="openweathermap",
    )


class TestAvgAqi:
    def test_average_of_multiple_readings(self, db, sample_city):
        db.add(_make_aq(sample_city.id, aqi=100, hours_ago=2))
        db.add(_make_aq(sample_city.id, aqi=60,  hours_ago=4))
        db.add(_make_aq(sample_city.id, aqi=80,  hours_ago=6))
        db.flush()

        avg = avg_aqi_last_n_hours(db, sample_city.id, hours=24)
        assert avg == pytest.approx(80.0, abs=0.1)

    def test_no_readings_returns_none(self, db, sample_city):
        avg = avg_aqi_last_n_hours(db, sample_city.id, hours=24)
        assert avg is None

    def test_readings_outside_window_excluded(self, db, sample_city):
        db.add(_make_aq(sample_city.id, aqi=200, hours_ago=50))  # outside 24h window
        db.add(_make_aq(sample_city.id, aqi=50,  hours_ago=10))  # inside
        db.flush()

        avg = avg_aqi_last_n_hours(db, sample_city.id, hours=24)
        assert avg == pytest.approx(50.0, abs=0.1)


class TestLatestReading:
    def test_latest_air_quality_returned(self, db, sample_city):
        db.add(_make_aq(sample_city.id, aqi=40, hours_ago=5))
        db.add(_make_aq(sample_city.id, aqi=90, hours_ago=1))  # most recent
        db.flush()

        latest = latest_air_quality(db, sample_city.id)
        assert latest is not None
        assert latest.aqi == 90

    def test_latest_weather_returned(self, db, sample_city):
        db.add(_make_weather(sample_city.id, temp=10.0, hours_ago=4))
        db.add(_make_weather(sample_city.id, temp=18.0, hours_ago=0.5))  # most recent
        db.flush()

        latest = latest_weather(db, sample_city.id)
        assert latest is not None
        assert latest.temperature == pytest.approx(18.0)

    def test_no_readings_returns_none(self, db, sample_city):
        assert latest_air_quality(db, sample_city.id) is None
        assert latest_weather(db, sample_city.id) is None
