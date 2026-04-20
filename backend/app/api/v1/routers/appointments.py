"""Appointment booking API endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.appointment import (
    AppointmentCancellationRequest,
    AppointmentCreateRequest,
    AppointmentRescheduleRequest,
    AppointmentResponse,
)
from app.schemas.suggestion import CriticalAppointmentSuggestionsResponse
from app.services.appointment_service import (
    AppointmentCancellationNotAllowedError,
    AppointmentNotFoundError,
    AppointmentRescheduleNotAllowedError,
    AppointmentSlotUnavailableError,
    AppointmentService,
    InvalidAppointmentDateError,
    SpecialistUnavailableError,
)
from app.services.suggestion_service import NoRecentCriticalAlertError, SuggestionService

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_appointment(
    payload: AppointmentCreateRequest,
    current_user: CurrentUser,
    db: DbSession,
) -> AppointmentResponse:
    """Create a new appointment request for the authenticated user."""

    service = AppointmentService(db)
    try:
        appointment = service.create_appointment(current_user, payload)
    except SpecialistUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidAppointmentDateError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except AppointmentSlotUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return AppointmentResponse.model_validate(appointment)


@router.get("")
def list_appointments(current_user: CurrentUser, db: DbSession) -> list[AppointmentResponse]:
    """List appointments owned by the authenticated user."""

    appointments = AppointmentService(db).list_appointments(current_user)
    return [AppointmentResponse.model_validate(item) for item in appointments]


@router.get("/suggestions/critical")
def list_critical_appointment_suggestions(
    current_user: CurrentUser,
    db: DbSession,
) -> CriticalAppointmentSuggestionsResponse:
    """Return live specialist slot suggestions for users with a recent critical alert."""

    service = SuggestionService(db)
    try:
        return service.get_critical_appointment_suggestions(current_user)
    except NoRecentCriticalAlertError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{appointment_id}")
def get_appointment(
    appointment_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
) -> AppointmentResponse:
    """Return one appointment owned by the authenticated user."""

    try:
        appointment = AppointmentService(db).get_appointment(current_user, appointment_id)
    except AppointmentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return AppointmentResponse.model_validate(appointment)


@router.patch("/{appointment_id}/cancel")
def cancel_appointment(
    appointment_id: UUID,
    payload: AppointmentCancellationRequest | None,
    current_user: CurrentUser,
    db: DbSession,
) -> AppointmentResponse:
    """Cancel an owned appointment if it is still mutable."""

    service = AppointmentService(db)
    try:
        appointment = service.cancel_appointment(current_user, appointment_id, payload)
    except AppointmentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AppointmentCancellationNotAllowedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return AppointmentResponse.model_validate(appointment)


@router.patch("/{appointment_id}/reschedule")
def reschedule_appointment(
    appointment_id: UUID,
    payload: AppointmentRescheduleRequest,
    current_user: CurrentUser,
    db: DbSession,
) -> AppointmentResponse:
    """Reschedule an owned appointment and move it back to requested state."""

    service = AppointmentService(db)
    try:
        appointment = service.reschedule_appointment(current_user, appointment_id, payload)
    except AppointmentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AppointmentRescheduleNotAllowedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except InvalidAppointmentDateError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except AppointmentSlotUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return AppointmentResponse.model_validate(appointment)
