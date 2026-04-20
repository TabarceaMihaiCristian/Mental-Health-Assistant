"""Health-related API endpoints, including database readiness checks."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.jobs.scheduler import get_scheduler_status


router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]


@router.get("", summary="Application health check")
def health_check() -> dict[str, str]:
    """Return a simple response indicating the API process is reachable."""

    return {"status": "ok"}


@router.get("/db", summary="Database health check")
def database_health_check(db: DbSession) -> dict[str, str]:
    """Verify that the database connection can execute a trivial query."""

    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc

    return {"status": "ok"}


@router.get("/scheduler", summary="Scheduler status")
def scheduler_health_check() -> dict[str, object]:
    """Return the current APScheduler runtime status and last job execution details."""

    return get_scheduler_status()
