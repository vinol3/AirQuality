from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CityOut(BaseModel):
    id: int
    name: str
    country: str
    latitude: float
    longitude: float

    model_config = {"from_attributes": True}


class AirQualityOut(BaseModel):
    id: int
    city_id: int
    recorded_at: datetime
    aqi: Optional[int]
    pm25: Optional[float]
    pm10: Optional[float]
    source: str

    model_config = {"from_attributes": True}


class WeatherOut(BaseModel):
    id: int
    city_id: int
    recorded_at: datetime
    temperature: Optional[float]
    humidity: Optional[int]
    wind_speed: Optional[float]
    pressure: Optional[int]
    description: Optional[str]
    source: str

    model_config = {"from_attributes": True}


class CityRanking(BaseModel):
    rank: int
    city: CityOut
    latest_aqi: Optional[int]
    avg_aqi_24h: Optional[float]
    aqi_category: str
    aqi_color: str


class CityDetail(BaseModel):
    city: CityOut
    latest_air_quality: Optional[AirQualityOut]
    latest_weather: Optional[WeatherOut]


class CorrelationResult(BaseModel):
    city: CityOut
    temperature_correlation: Optional[float]
    humidity_correlation: Optional[float]
    wind_speed_correlation: Optional[float]
    pressure_correlation: Optional[float]
    data_points: int


class HealthResponse(BaseModel):
    status: str
    env: str
    db_ok: bool
