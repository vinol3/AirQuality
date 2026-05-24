"""
AirPulse — FastAPI Application Entry Point
==========================================
Wires together all layers:
  1. DB table creation + city seeding on startup
  2. APScheduler for periodic data ingestion
  3. All API routers registered under /api/v1
  4. CORS middleware (permissive in dev, tighten for prod)
  5. Structured JSON logging via structlog
"""
import logging
import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.database import create_tables, SessionLocal
from app.seeds import seed_cities
from app.scheduler import start_scheduler, stop_scheduler, run_ingestion_cycle
from app.api.routes import cities, air_quality, weather, rankings, correlations, admin

# ── Logging setup ─────────────────────────────────────────────────────────────

logging.basicConfig(level=settings.LOG_LEVEL.upper())

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    ),
    logger_factory=structlog.PrintLoggerFactory(),
)

log = structlog.get_logger()


# ── Application lifespan ──────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    log.info("airpulse_starting", env=settings.ENV)

    # 1. Create DB tables (idempotent)
    create_tables()

    # 2. Seed initial cities
    db = SessionLocal()
    try:
        seed_cities(db)
    finally:
        db.close()

    # 3. Run an immediate ingestion cycle so the dashboard has data right away
    await run_ingestion_cycle()

    # 4. Start the recurring scheduler
    start_scheduler()

    log.info("airpulse_ready", swagger_url="http://localhost/docs")

    yield  # ← application runs here

    stop_scheduler()
    log.info("airpulse_shutdown")


# ── FastAPI app ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="AirPulse API",
    description=(
        "European Air Quality & Weather Dashboard.\n\n"
        "Aggregates data from **IQAir** and **OpenWeatherMap** into a unified REST API."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow the nginx-served frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENV != "prod" else ["http://localhost"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ── Register routers ──────────────────────────────────────────────────────────

API_PREFIX = "/api/v1"

app.include_router(cities.router, prefix=API_PREFIX)
app.include_router(air_quality.router, prefix=API_PREFIX)
app.include_router(weather.router, prefix=API_PREFIX)
app.include_router(rankings.router, prefix=API_PREFIX)
app.include_router(correlations.router, prefix=API_PREFIX)
app.include_router(admin.router, prefix=API_PREFIX)
