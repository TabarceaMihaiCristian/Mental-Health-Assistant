"""Specialist directory API endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.authorization import require_specialist_user
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.specialist import (
    SpecialistResponse,
    SpecialistReviewResponse,
    SpecialistReviewUpsertRequest,
)
from app.schemas.availability import (
    SpecialistCalendarResponse,
    SpecialistAvailabilityResponse,
    SpecialistAvailabilitySlotResponse,
)
from app.schemas.specialist_schedule import (
    AvailabilityRuleResponse,
    AvailabilityRuleUpsertRequest,
    BreakCreateRequest,
    BreakResponse,
    BreakUpdateRequest,
    TimeOffCreateRequest,
    TimeOffResponse,
    TimeOffUpdateRequest,
)
from app.services.specialist_service import (
    SpecialistNotFoundError,
    SpecialistReviewAlreadyExistsError,
    SpecialistReviewNotFoundError,
    SpecialistService,
)
from app.services.specialist_schedule_service import (
    SpecialistProfileNotFoundError,
    SpecialistScheduleItemNotFoundError,
    SpecialistScheduleService,
    SpecialistScheduleValidationError,
)
from app.services.availability_service import (
    AvailabilityService,
    AvailabilityWindowError,
    SpecialistAvailabilityNotFoundError,
)

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
SpecialistUser = Annotated[User, Depends(require_specialist_user)]


@router.get("")
def list_specialists(_: CurrentUser, db: DbSession) -> list[SpecialistResponse]:
    """List active specialists with computed ratings for authenticated users."""

    specialists = SpecialistService(db).list_specialists()
    return [SpecialistResponse.model_validate(item) for item in specialists]


@router.get("/{specialist_id}")
def get_specialist(
    specialist_id: UUID,
    _: CurrentUser,
    db: DbSession,
) -> SpecialistResponse:
    """Return a single active specialist with aggregated review metadata."""

    service = SpecialistService(db)
    try:
        specialist = service.get_specialist(specialist_id)
    except SpecialistNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return SpecialistResponse.model_validate(specialist)


@router.get("/{specialist_id}/availability")
def get_specialist_availability(
    specialist_id: UUID,
    _: CurrentUser,
    db: DbSession,
    date_from: date,
    date_to: date,
) -> SpecialistAvailabilityResponse:
    """Return bookable 2-hour slots for a specialist within a date range."""

    service = AvailabilityService(db)
    try:
        slots = service.get_available_slots(specialist_id, date_from, date_to)
    except SpecialistAvailabilityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AvailabilityWindowError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return SpecialistAvailabilityResponse(
        specialist_id=specialist_id,
        date_from=date_from,
        date_to=date_to,
        slots=[
            SpecialistAvailabilitySlotResponse(
                start_datetime=slot.start_datetime,
                end_datetime=slot.end_datetime,
            )
            for slot in slots
        ],
    )


@router.post(
    "/{specialist_id}/reviews",
    status_code=status.HTTP_201_CREATED,
)
def create_specialist_review(
    specialist_id: UUID,
    payload: SpecialistReviewUpsertRequest,
    current_user: CurrentUser,
    db: DbSession,
) -> SpecialistReviewResponse:
    """Create a new review for an active specialist."""

    service = SpecialistService(db)
    try:
        review = service.create_review(current_user, specialist_id, payload)
    except SpecialistNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except SpecialistReviewAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return SpecialistReviewResponse.model_validate(review)


@router.put("/{specialist_id}/reviews/me")
def update_my_specialist_review(
    specialist_id: UUID,
    payload: SpecialistReviewUpsertRequest,
    current_user: CurrentUser,
    db: DbSession,
) -> SpecialistReviewResponse:
    """Update the current user's review for an active specialist."""

    service = SpecialistService(db)
    try:
        review = service.update_my_review(current_user, specialist_id, payload)
    except SpecialistNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except SpecialistReviewNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return SpecialistReviewResponse.model_validate(review)


@router.get("/me/availability")
def list_my_availability(
    current_user: SpecialistUser,
    db: DbSession,
) -> list[AvailabilityRuleResponse]:
    """List recurring weekly availability rules for the current specialist."""

    try:
        rules = SpecialistScheduleService(db).list_availability_rules(current_user)
    except SpecialistProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return [AvailabilityRuleResponse.model_validate(item) for item in rules]


@router.get("/me/calendar")
def get_my_calendar(
    current_user: SpecialistUser,
    db: DbSession,
    date_from: date,
    date_to: date,
) -> SpecialistCalendarResponse:
    """Return appointments, slots, breaks, and time off for the current specialist."""

    service = SpecialistScheduleService(db)
    try:
        appointments, slots, specialist_breaks, periods, specialist_id = service.get_calendar(
            current_user,
            date_from,
            date_to,
        )
    except SpecialistProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AvailabilityWindowError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return SpecialistCalendarResponse(
        specialist_id=specialist_id,
        date_from=date_from,
        date_to=date_to,
        appointments=list(appointments),
        available_slots=[
            SpecialistAvailabilitySlotResponse(
                start_datetime=slot.start_datetime,
                end_datetime=slot.end_datetime,
            )
            for slot in slots
        ],
        breaks=[BreakResponse.model_validate(item) for item in specialist_breaks],
        time_off_periods=[TimeOffResponse.model_validate(item) for item in periods],
    )


@router.put("/me/availability")
def replace_my_availability(
    payload: list[AvailabilityRuleUpsertRequest],
    current_user: SpecialistUser,
    db: DbSession,
) -> list[AvailabilityRuleResponse]:
    """Replace recurring weekly availability rules for the current specialist."""

    service = SpecialistScheduleService(db)
    try:
        rules = service.replace_availability_rules(current_user, payload)
    except SpecialistProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except SpecialistScheduleValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return [AvailabilityRuleResponse.model_validate(item) for item in rules]


@router.get("/me/breaks")
def list_my_breaks(
    current_user: SpecialistUser,
    db: DbSession,
) -> list[BreakResponse]:
    """List recurring break windows for the current specialist."""

    try:
        specialist_breaks = SpecialistScheduleService(db).list_breaks(current_user)
    except SpecialistProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return [BreakResponse.model_validate(item) for item in specialist_breaks]


@router.post("/me/breaks", status_code=status.HTTP_201_CREATED)
def create_my_break(
    payload: BreakCreateRequest,
    current_user: SpecialistUser,
    db: DbSession,
) -> BreakResponse:
    """Create a recurring break window for the current specialist."""

    service = SpecialistScheduleService(db)
    try:
        specialist_break = service.create_break(current_user, payload)
    except SpecialistProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except SpecialistScheduleValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return BreakResponse.model_validate(specialist_break)


@router.put("/me/breaks/{break_id}")
def update_my_break(
    break_id: UUID,
    payload: BreakUpdateRequest,
    current_user: SpecialistUser,
    db: DbSession,
) -> BreakResponse:
    """Update a recurring break window for the current specialist."""

    service = SpecialistScheduleService(db)
    try:
        specialist_break = service.update_break(current_user, break_id, payload)
    except SpecialistProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except SpecialistScheduleItemNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except SpecialistScheduleValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return BreakResponse.model_validate(specialist_break)


@router.delete("/me/breaks/{break_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_break(
    break_id: UUID,
    current_user: SpecialistUser,
    db: DbSession,
) -> None:
    """Delete a recurring break window for the current specialist."""

    service = SpecialistScheduleService(db)
    try:
        service.delete_break(current_user, break_id)
    except SpecialistProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except SpecialistScheduleItemNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/me/time-off")
def list_my_time_off(
    current_user: SpecialistUser,
    db: DbSession,
) -> list[TimeOffResponse]:
    """List time-off windows for the current specialist."""

    try:
        periods = SpecialistScheduleService(db).list_time_off(current_user)
    except SpecialistProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return [TimeOffResponse.model_validate(item) for item in periods]


@router.post("/me/time-off", status_code=status.HTTP_201_CREATED)
def create_my_time_off(
    payload: TimeOffCreateRequest,
    current_user: SpecialistUser,
    db: DbSession,
) -> TimeOffResponse:
    """Create a time-off window for the current specialist."""

    service = SpecialistScheduleService(db)
    try:
        period = service.create_time_off(current_user, payload)
    except SpecialistProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (SpecialistScheduleValidationError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return TimeOffResponse.model_validate(period)


@router.put("/me/time-off/{time_off_id}")
def update_my_time_off(
    time_off_id: UUID,
    payload: TimeOffUpdateRequest,
    current_user: SpecialistUser,
    db: DbSession,
) -> TimeOffResponse:
    """Update a time-off window for the current specialist."""

    service = SpecialistScheduleService(db)
    try:
        period = service.update_time_off(current_user, time_off_id, payload)
    except SpecialistProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except SpecialistScheduleItemNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (SpecialistScheduleValidationError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return TimeOffResponse.model_validate(period)


@router.delete("/me/time-off/{time_off_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_time_off(
    time_off_id: UUID,
    current_user: SpecialistUser,
    db: DbSession,
) -> None:
    """Delete a time-off window for the current specialist."""

    service = SpecialistScheduleService(db)
    try:
        service.delete_time_off(current_user, time_off_id)
    except SpecialistProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except SpecialistScheduleItemNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
