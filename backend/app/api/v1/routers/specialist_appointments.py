"""Specialist-side appointment management endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.authorization import require_specialist_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.appointment import (
    AppointmentRejectionRequest,
    AppointmentRescheduleRequest,
    AppointmentResponse,
    SpecialistAppointmentCreateRequest,
)
from app.services.appointment_service import (
    AppointmentCompletionNotAllowedError,
    AppointmentDecisionNotAllowedError,
    AppointmentNotFoundError,
    AppointmentRescheduleNotAllowedError,
    AppointmentService,
    AppointmentSlotUnavailableError,
    AppointmentUserNotFoundError,
    InvalidAppointmentDateError,
    SpecialistProfileNotFoundError,
)

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]
SpecialistUser = Annotated[User, Depends(require_specialist_user)]


@router.get("")
def list_specialist_appointments(
    current_user: SpecialistUser,
    db: DbSession,
) -> list[AppointmentResponse]:
    """List appointments assigned to the authenticated specialist."""

    try:
        appointments = AppointmentService(db).list_specialist_appointments(current_user)
    except SpecialistProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return [AppointmentResponse.model_validate(item) for item in appointments]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_specialist_appointment(
    payload: SpecialistAppointmentCreateRequest,
    current_user: SpecialistUser,
    db: DbSession,
) -> AppointmentResponse:
    """Create an appointment for a user on behalf of the authenticated specialist."""

    service = AppointmentService(db)
    try:
        appointment = service.create_specialist_appointment(current_user, payload)
    except SpecialistProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AppointmentUserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidAppointmentDateError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except AppointmentSlotUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return AppointmentResponse.model_validate(appointment)


@router.get("/{appointment_id}")
def get_specialist_appointment(
    appointment_id: UUID,
    current_user: SpecialistUser,
    db: DbSession,
) -> AppointmentResponse:
    """Return one appointment assigned to the authenticated specialist."""

    service = AppointmentService(db)
    try:
        appointment = service.get_specialist_appointment(current_user, appointment_id)
    except SpecialistProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AppointmentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return AppointmentResponse.model_validate(appointment)


@router.patch("/{appointment_id}/confirm")
def confirm_specialist_appointment(
    appointment_id: UUID,
    current_user: SpecialistUser,
    db: DbSession,
) -> AppointmentResponse:
    """Confirm a requested appointment on behalf of the specialist."""

    service = AppointmentService(db)
    try:
        appointment = service.confirm_specialist_appointment(current_user, appointment_id)
    except SpecialistProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AppointmentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AppointmentDecisionNotAllowedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return AppointmentResponse.model_validate(appointment)


@router.patch("/{appointment_id}/reject")
def reject_specialist_appointment(
    appointment_id: UUID,
    payload: AppointmentRejectionRequest,
    current_user: SpecialistUser,
    db: DbSession,
) -> AppointmentResponse:
    """Reject a requested appointment on behalf of the specialist."""

    service = AppointmentService(db)
    try:
        appointment = service.reject_specialist_appointment(
            current_user,
            appointment_id,
            payload,
        )
    except SpecialistProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AppointmentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AppointmentDecisionNotAllowedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return AppointmentResponse.model_validate(appointment)


@router.patch("/{appointment_id}/reschedule")
def reschedule_specialist_appointment(
    appointment_id: UUID,
    payload: AppointmentRescheduleRequest,
    current_user: SpecialistUser,
    db: DbSession,
) -> AppointmentResponse:
    """Reschedule an appointment on behalf of the specialist."""

    service = AppointmentService(db)
    try:
        appointment = service.reschedule_specialist_appointment(
            current_user,
            appointment_id,
            payload,
        )
    except SpecialistProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AppointmentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AppointmentRescheduleNotAllowedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except (InvalidAppointmentDateError, AppointmentSlotUnavailableError) as exc:
        status_code = (
            status.HTTP_400_BAD_REQUEST
            if isinstance(exc, InvalidAppointmentDateError)
            else status.HTTP_409_CONFLICT
        )
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    return AppointmentResponse.model_validate(appointment)


@router.patch("/{appointment_id}/complete")
def complete_specialist_appointment(
    appointment_id: UUID,
    current_user: SpecialistUser,
    db: DbSession,
) -> AppointmentResponse:
    """Mark a confirmed appointment as completed."""

    service = AppointmentService(db)
    try:
        appointment = service.complete_specialist_appointment(current_user, appointment_id)
    except SpecialistProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AppointmentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AppointmentCompletionNotAllowedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return AppointmentResponse.model_validate(appointment)
