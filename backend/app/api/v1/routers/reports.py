"""Mood reporting API endpoints."""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.enums import ReportPeriod
from app.models.user import User
from app.schemas.mood_analysis import DailyMoodSummaryResponse, ReportResponse
from app.services.report_service import ReportService


router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/daily-summaries")
def list_daily_mood_summaries(
    current_user: CurrentUser,
    db: DbSession,
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
) -> list[DailyMoodSummaryResponse]:
    """List stored daily mood summaries for the authenticated user."""

    summaries = ReportService(db).list_daily_summaries(current_user, date_from, date_to)
    return [DailyMoodSummaryResponse.model_validate(summary) for summary in summaries]


@router.get("/{period}")
def get_period_report(
    period: ReportPeriod,
    current_user: CurrentUser,
    db: DbSession,
    reference_date: Annotated[date | None, Query()] = None,
) -> ReportResponse:
    """Return an already-generated weekly or monthly report for the authenticated user."""

    effective_date = reference_date or datetime.now(UTC).date()
    report = ReportService(db).get_report(current_user, period, effective_date)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found for the requested period.",
        )
    return ReportResponse.model_validate(report)


@router.post("/{period}", status_code=status.HTTP_201_CREATED)
def generate_period_report(
    period: ReportPeriod,
    current_user: CurrentUser,
    db: DbSession,
    reference_date: Annotated[date | None, Query()] = None,
) -> ReportResponse:
    """Generate and persist a weekly or monthly report for the authenticated user."""

    effective_date = reference_date or datetime.now(UTC).date()
    report = ReportService(db).generate_report(current_user, period, effective_date)
    return ReportResponse.model_validate(report)
