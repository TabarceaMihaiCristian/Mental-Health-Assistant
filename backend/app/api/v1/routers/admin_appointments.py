"""Admin endpoints for appointment oversight views."""

from __future__ import annotations

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.authorization import require_admin_user
from app.db.session import get_db
from app.models.enums import AppointmentStatus
from app.models.user import User
from app.schemas.appointment import AppointmentPageResponse, AppointmentResponse
from app.services.appointment_service import AppointmentNotFoundError, AppointmentService

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]
AdminUser = Annotated[User, Depends(require_admin_user)]


@router.get("")
def list_appointments(
    _: AdminUser,
    db: DbSession,
    status_filter: Annotated[AppointmentStatus | None, Query(alias="status")] = None,
    specialist_id: Annotated[UUID | None, Query()] = None,
    user_id: Annotated[UUID | None, Query()] = None,
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 50,
) -> AppointmentPageResponse:
    """List all appointments for admin oversight."""

    appointments, total = AppointmentService(db).list_filtered_appointments(
        status=status_filter,
        specialist_id=specialist_id,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return AppointmentPageResponse(
        items=[AppointmentResponse.model_validate(item) for item in appointments],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


@router.get("/{appointment_id}")
def get_appointment(
    appointment_id: UUID,
    _: AdminUser,
    db: DbSession,
) -> AppointmentResponse:
    """Return one appointment by id for admin oversight."""

    try:
        appointment = AppointmentService(db).get_any_appointment(appointment_id)
    except AppointmentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return AppointmentResponse.model_validate(appointment)
