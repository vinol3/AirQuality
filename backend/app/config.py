from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Runtime environment
    ENV: str = "dev"

    DATABASE_URL: str = "postgresql://airpulse:airpulse@db:5432/airpulse_dev"

    REDIS_URL: str = "redis://redis:6379"

    IQAIR_API_KEY: str = "demo"
    OPENWEATHER_API_KEY: str = "demo"

    INGESTION_INTERVAL_MINUTES: int = 30

    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
