"""Unit tests for specialist directory and schedule router branches."""

from __future__ import annotations

from datetime import UTC, datetime, time
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.v1.routers import specialists as router
from app.models.enums import SpecialistStatus, UserRole
from app.models.user import User
from app.schemas.specialist import SpecialistReviewUpsertRequest
from app.schemas.specialist_schedule import (
    AvailabilityRuleUpsertRequest,
    BreakCreateRequest,
    BreakUpdateRequest,
    TimeOffCreateRequest,
    TimeOffUpdateRequest,
)
from app.services.availability_service import AvailabilityWindowError, SpecialistAvailabilityNotFoundError
from app.services.specialist_schedule_service import (
    SpecialistProfileNotFoundError,
    SpecialistScheduleItemNotFoundError,
    SpecialistScheduleValidationError,
)
from app.services.specialist_service import (
    SpecialistNotFoundError,
    SpecialistReviewAlreadyExistsError,
    SpecialistReviewNotFoundError,
)


def _current_user(*, role: UserRole = UserRole.USER) -> User:
    return User(email=f"{uuid4().hex[:12]}@example.com", full_name="Router Test User", role=role)


def _specialist_item() -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid4(),
        full_name="Dr. Specialist",
        specialty="Psychology",
        bio="Helpful bio",
        consultation_modes=["online"],
        city="Bucharest",
        status=SpecialistStatus.ACTIVE,
        average_rating=4.7,
        review_count=6,
    )


def _review_item() -> SimpleNamespace:
    return SimpleNamespace(id=uuid4(), specialist_id=uuid4(), user_id=uuid4(), rating=5, comment="Helpful")


@pytest.mark.unit
def test_public_specialist_routes_cover_success_and_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    specialist = _specialist_item()
    current_user = _current_user()
    monkeypatch.setattr(router.SpecialistResponse, "model_validate", classmethod(lambda cls, item: item))
    service = SimpleNamespace(list_specialists=Mock(return_value=[specialist]), get_specialist=Mock(return_value=specialist))
    monkeypatch.setattr(router, "SpecialistService", Mock(return_value=service))

    assert router.list_specialists(current_user, Mock()) == [specialist]
    assert router.get_specialist(specialist.id, current_user, Mock()) is specialist

    failing = SimpleNamespace(get_specialist=Mock(side_effect=SpecialistNotFoundError("Missing specialist")))
    monkeypatch.setattr(router, "SpecialistService", Mock(return_value=failing))
    with pytest.raises(HTTPException) as error:
        router.get_specialist(uuid4(), current_user, Mock())
    assert error.value.status_code == 404
    assert error.value.detail == "Missing specialist"


@pytest.mark.unit
def test_specialist_availability_route_maps_window_and_missing_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    slot = SimpleNamespace(start_datetime=datetime(2026, 4, 25, 9, tzinfo=UTC), end_datetime=datetime(2026, 4, 25, 11, tzinfo=UTC))
    current_user = _current_user()
    service = SimpleNamespace(get_available_slots=Mock(return_value=[slot]))
    monkeypatch.setattr(router, "AvailabilityService", Mock(return_value=service))
    specialist_id = uuid4()

    result = router.get_specialist_availability(
        specialist_id,
        current_user,
        Mock(),
        datetime(2026, 4, 25, tzinfo=UTC).date(),
        datetime(2026, 4, 26, tzinfo=UTC).date(),
    )

    assert result.specialist_id == specialist_id
    assert len(result.slots) == 1

    for exc, status_code in [
        (SpecialistAvailabilityNotFoundError("Missing availability"), 404),
        (AvailabilityWindowError("Bad window"), 400),
    ]:
        failing = SimpleNamespace(get_available_slots=Mock(side_effect=exc))
        monkeypatch.setattr(router, "AvailabilityService", Mock(return_value=failing))
        with pytest.raises(HTTPException) as error:
            router.get_specialist_availability(
                specialist_id,
                current_user,
                Mock(),
                datetime(2026, 4, 25, tzinfo=UTC).date(),
                datetime(2026, 4, 26, tzinfo=UTC).date(),
            )
        assert error.value.status_code == status_code
        assert error.value.detail == str(exc)


@pytest.mark.unit
def test_specialist_review_routes_cover_duplicate_and_missing_cases(monkeypatch: pytest.MonkeyPatch) -> None:
    review = _review_item()
    payload = SpecialistReviewUpsertRequest(rating=5, comment="Helpful")
    current_user = _current_user()
    monkeypatch.setattr(router.SpecialistReviewResponse, "model_validate", classmethod(lambda cls, item: item))
    service = SimpleNamespace(create_review=Mock(return_value=review), update_my_review=Mock(return_value=review))
    monkeypatch.setattr(router, "SpecialistService", Mock(return_value=service))

    assert router.create_specialist_review(uuid4(), payload, current_user, Mock()) is review
    assert router.update_my_specialist_review(uuid4(), payload, current_user, Mock()) is review

    cases = [
        ("create_review", SpecialistNotFoundError("Missing specialist"), 404),
        ("create_review", SpecialistReviewAlreadyExistsError("Duplicate review"), 400),
        ("update_my_review", SpecialistNotFoundError("Missing specialist"), 404),
        ("update_my_review", SpecialistReviewNotFoundError("Missing review"), 404),
    ]
    for method_name, exc, status_code in cases:
        failing = SimpleNamespace(**{method_name: Mock(side_effect=exc)})
        monkeypatch.setattr(router, "SpecialistService", Mock(return_value=failing))
        with pytest.raises(HTTPException) as error:
            if method_name == "create_review":
                router.create_specialist_review(uuid4(), payload, current_user, Mock())
            else:
                router.update_my_specialist_review(uuid4(), payload, current_user, Mock())
        assert error.value.status_code == status_code
        assert error.value.detail == str(exc)


@pytest.mark.unit
def test_specialist_schedule_routes_cover_success_and_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    rule = SimpleNamespace(id=uuid4(), specialist_id=uuid4(), weekday=1, start_time=time(hour=9), end_time=time(hour=12), is_enabled=True)
    specialist_break = SimpleNamespace(id=uuid4(), specialist_id=uuid4(), weekday=1, start_time=time(hour=12), end_time=time(hour=13), label="Lunch")
    time_off = SimpleNamespace(id=uuid4(), specialist_id=uuid4(), start_datetime=datetime(2026, 4, 28, 9, tzinfo=UTC), end_datetime=datetime(2026, 4, 28, 17, tzinfo=UTC), reason="Vacation")
    slot = SimpleNamespace(start_datetime=datetime(2026, 4, 25, 9, tzinfo=UTC), end_datetime=datetime(2026, 4, 25, 11, tzinfo=UTC))
    appointment = SimpleNamespace(id=uuid4())
    current_user = _current_user(role=UserRole.SPECIALIST)
    availability_payload = AvailabilityRuleUpsertRequest(weekday=1, start_time=time(hour=9), end_time=time(hour=12), is_enabled=True)
    break_create_payload = BreakCreateRequest(weekday=1, start_time=time(hour=12), end_time=time(hour=13), label="Lunch")
    break_update_payload = BreakUpdateRequest(weekday=1, start_time=time(hour=13), end_time=time(hour=14), label="Tea")
    time_off_create_payload = TimeOffCreateRequest(
        start_datetime=datetime(2026, 4, 28, 9, tzinfo=UTC),
        end_datetime=datetime(2026, 4, 28, 17, tzinfo=UTC),
        reason="Vacation",
    )
    time_off_update_payload = TimeOffUpdateRequest(
        start_datetime=datetime(2026, 4, 29, 9, tzinfo=UTC),
        end_datetime=datetime(2026, 4, 29, 17, tzinfo=UTC),
        reason="Updated",
    )
    monkeypatch.setattr(router.AvailabilityRuleResponse, "model_validate", classmethod(lambda cls, item: item))
    monkeypatch.setattr(router.BreakResponse, "model_validate", classmethod(lambda cls, item: item))
    monkeypatch.setattr(router.TimeOffResponse, "model_validate", classmethod(lambda cls, item: item))
    monkeypatch.setattr(router, "SpecialistCalendarResponse", lambda **kwargs: SimpleNamespace(**kwargs))
    service = SimpleNamespace(
        list_availability_rules=Mock(return_value=[rule]),
        get_calendar=Mock(return_value=([appointment], [slot], [specialist_break], [time_off], rule.specialist_id)),
        replace_availability_rules=Mock(return_value=[rule]),
        list_breaks=Mock(return_value=[specialist_break]),
        create_break=Mock(return_value=specialist_break),
        update_break=Mock(return_value=specialist_break),
        list_time_off=Mock(return_value=[time_off]),
        create_time_off=Mock(return_value=time_off),
        update_time_off=Mock(return_value=time_off),
        delete_break=Mock(return_value=None),
        delete_time_off=Mock(return_value=None),
    )
    monkeypatch.setattr(router, "SpecialistScheduleService", Mock(return_value=service))

    assert router.list_my_availability(current_user, Mock()) == [rule]
    calendar = router.get_my_calendar(current_user, Mock(), datetime(2026, 4, 25, tzinfo=UTC).date(), datetime(2026, 4, 26, tzinfo=UTC).date())
    assert calendar.specialist_id == rule.specialist_id
    assert len(router.replace_my_availability([availability_payload], current_user, Mock())) == 1
    assert router.list_my_breaks(current_user, Mock()) == [specialist_break]
    assert router.create_my_break(break_create_payload, current_user, Mock()) is specialist_break
    assert router.update_my_break(specialist_break.id, break_update_payload, current_user, Mock()) is specialist_break
    router.delete_my_break(specialist_break.id, current_user, Mock())
    assert router.list_my_time_off(current_user, Mock()) == [time_off]
    assert router.create_my_time_off(time_off_create_payload, current_user, Mock()) is time_off
    assert router.update_my_time_off(time_off.id, time_off_update_payload, current_user, Mock()) is time_off
    router.delete_my_time_off(time_off.id, current_user, Mock())

    error_cases = [
        ("list_availability_rules", SpecialistProfileNotFoundError("No profile"), 404, lambda: router.list_my_availability(current_user, Mock())),
        ("get_calendar", AvailabilityWindowError("Bad window"), 400, lambda: router.get_my_calendar(current_user, Mock(), datetime(2026, 4, 25, tzinfo=UTC).date(), datetime(2026, 4, 26, tzinfo=UTC).date())),
        ("replace_availability_rules", SpecialistScheduleValidationError("Overlap"), 400, lambda: router.replace_my_availability([availability_payload], current_user, Mock())),
        ("create_break", SpecialistScheduleValidationError("Break overlap"), 400, lambda: router.create_my_break(break_create_payload, current_user, Mock())),
        ("update_break", SpecialistScheduleItemNotFoundError("Break not found."), 404, lambda: router.update_my_break(uuid4(), break_update_payload, current_user, Mock())),
        ("delete_break", SpecialistScheduleItemNotFoundError("Break not found."), 404, lambda: router.delete_my_break(uuid4(), current_user, Mock())),
        ("create_time_off", ValueError("Invalid future datetime"), 400, lambda: router.create_my_time_off(time_off_create_payload, current_user, Mock())),
        ("update_time_off", SpecialistScheduleValidationError("Bad time off"), 400, lambda: router.update_my_time_off(uuid4(), time_off_update_payload, current_user, Mock())),
        ("delete_time_off", SpecialistScheduleItemNotFoundError("Time off not found."), 404, lambda: router.delete_my_time_off(uuid4(), current_user, Mock())),
    ]

    for method_name, exc, status_code, invoke in error_cases:
        failing = SimpleNamespace(**{method_name: Mock(side_effect=exc)})
        monkeypatch.setattr(router, "SpecialistScheduleService", Mock(return_value=failing))
        with pytest.raises(HTTPException) as error:
            invoke()
        assert error.value.status_code == status_code
        assert error.value.detail == str(exc)
