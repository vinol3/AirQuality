import asyncio
import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.config import settings
from app.models.database import SessionLocal
from app.models.city import City
from app.models.air_quality import AirQualityReading
from app.models.weather import WeatherReading
from app.ingestion.iqair_client import fetch_city_air_quality
from app.ingestion.openweather_client import fetch_city_weather
from app.processing.normaliser import normalise_air_quality, normalise_weather

log = structlog.get_logger()

scheduler = AsyncIOScheduler()


async def run_ingestion_cycle() -> None:
    log.info("ingestion_cycle_start")
    db = SessionLocal()
    try:
        cities = db.query(City).all()
        tasks = [_ingest_city(db, city) for city in cities]
        await asyncio.gather(*tasks, return_exceptions=True)
        db.commit()
        log.info("ingestion_cycle_complete", city_count=len(cities))
    except Exception as exc:
        log.error("ingestion_cycle_failed", error=str(exc))
        db.rollback()
    finally:
        db.close()


async def _ingest_city(db, city: City) -> None:
    """Fetch and store one cycle of readings for a single city."""
    aq_raw = await fetch_city_air_quality(
        city=city.iqair_city,
        state=city.iqair_state,
        country=city.iqair_country,
        api_key=settings.IQAIR_API_KEY,
    )
    weather_raw = await fetch_city_weather(
        lat=city.latitude,
        lon=city.longitude,
        api_key=settings.OPENWEATHER_API_KEY,
        city_name=city.name,
    )

    if aq_raw:
        aq_record = normalise_air_quality(city.id, aq_raw)
        if aq_record:
            db.add(aq_record)

    if weather_raw:
        w_record = normalise_weather(city.id, weather_raw)
        if w_record:
            db.add(w_record)

    await asyncio.sleep(8)


def start_scheduler() -> None:
    scheduler.add_job(
        run_ingestion_cycle,
        trigger="interval",
        minutes=settings.INGESTION_INTERVAL_MINUTES,
        id="ingestion_cycle",
        replace_existing=True,
    )
    scheduler.start()
    log.info(
        "scheduler_started",
        interval_minutes=settings.INGESTION_INTERVAL_MINUTES,
    )


def stop_scheduler() -> None:
    scheduler.shutdown(wait=False)
    log.info("scheduler_stopped")
