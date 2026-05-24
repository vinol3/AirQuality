import structlog
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.schemas import HealthResponse
from app.config import settings

log = structlog.get_logger()
router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/health", response_model=HealthResponse, summary="Service health check")
def health_check(db: Session = Depends(get_db)):
    db_ok = True
    try:
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
    except Exception:
        db_ok = False

    return HealthResponse(status="ok" if db_ok else "degraded", env=settings.ENV, db_ok=db_ok)


@router.post("/refresh", summary="Manually trigger a data ingestion cycle")
async def manual_refresh(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    from app.scheduler import run_ingestion_cycle

    background_tasks.add_task(run_ingestion_cycle)
    log.info("manual_refresh_triggered")
    return {"message": "Ingestion cycle started in background"}
