"""Unit tests for admin-managed specialist onboarding workflows."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.models.enums import SpecialistStatus
from app.schemas.admin_specialist import (
    AdminSpecialistCreateRequest,
    AdminSpecialistStatusUpdateRequest,
    AdminSpecialistUpdateRequest,
)
from app.services.admin_specialist_service import (
    AdminSpecialistService,
    SpecialistOnboardingConflictError,
)
from tests.fixtures.auth import TEST_AUTH_SECRET

PASSWORD_FIELD = "password"


@pytest.mark.unit
def test_create_specialist_rejects_existing_local_identity() -> None:
    """Reject onboarding when the email is already linked to a local identity."""

    service = object.__new__(AdminSpecialistService)
    service.uow = Mock()
    service.user_repository = Mock()
    service.identity_repository = Mock()
    service.specialist_repository = Mock()
    service.logger = Mock()
    payload = AdminSpecialistCreateRequest(**{
        "email": "doctor@example.com",
        "full_name": "Dr. Existing",
        PASSWORD_FIELD: TEST_AUTH_SECRET,
        "specialty": "Psychology",
        "consultation_modes": ["online"],
        "bio": None,
        "city": None,
    })
    service.identity_repository.get_local_identity_by_email.return_value = object()

    with pytest.raises(
        SpecialistOnboardingConflictError,
        match="A user with this email already exists.",
    ):
        service.create_specialist(payload)


@pytest.mark.unit
def test_create_specialist_creates_user_identity_and_profile(monkeypatch: pytest.MonkeyPatch) -> None:
    """Persist all onboarding records and refresh the created specialist."""

    service = object.__new__(AdminSpecialistService)
    service.uow = Mock()
    service.user_repository = Mock()
    service.identity_repository = Mock()
    service.specialist_repository = Mock()
    service.logger = Mock()
    service.identity_repository.get_local_identity_by_email.return_value = None
    payload = AdminSpecialistCreateRequest(**{
        "email": " Doctor@Example.com ",
        "full_name": "  Dr. Example  ",
        PASSWORD_FIELD: TEST_AUTH_SECRET,
        "specialty": " Psychology ",
        "consultation_modes": ["online", "in_person"],
        "bio": "  Supportive specialist.  ",
        "city": "  Bucharest  ",
    })

    monkeypatch.setattr("app.services.admin_specialist_service.normalize_email", lambda value: value.strip().lower())
    monkeypatch.setattr("app.services.admin_specialist_service.normalize_full_name", lambda value: value.strip())
    monkeypatch.setattr("app.services.admin_specialist_service.normalize_optional_comment", lambda value: None if value is None else value.strip())
    monkeypatch.setattr("app.services.admin_specialist_service.hash_password", lambda value: f"hashed::{value}")

    created_user = None

    def add_user(user) -> None:
        nonlocal created_user
        created_user = user
        user.id = uuid4()

    created_identity = None

    def add_identity(identity) -> None:
        nonlocal created_identity
        created_identity = identity

    created_specialist = None

    def add_specialist(specialist) -> None:
        nonlocal created_specialist
        created_specialist = specialist
        specialist.id = uuid4()

    service.user_repository.add.side_effect = add_user
    service.identity_repository.add.side_effect = add_identity
    service.specialist_repository.add.side_effect = add_specialist

    result = service.create_specialist(payload)

    assert created_specialist
    assert result is created_specialist
    assert created_user
    assert created_user.email == "doctor@example.com"
    assert created_user.full_name == "Dr. Example"
    assert created_identity
    assert created_identity.user_id == created_user.id
    assert created_identity.password_hash == f"hashed::{TEST_AUTH_SECRET}"
    assert created_specialist.user_id == created_user.id
    assert created_specialist.full_name == "Dr. Example"
    assert created_specialist.specialty == "Psychology"
    assert created_specialist.bio == "Supportive specialist."
    assert created_specialist.city == "Bucharest"
    service.uow.commit.assert_called_once()
    service.uow.refresh.assert_called_once_with(created_specialist)


@pytest.mark.unit
def test_update_specialist_updates_only_supplied_fields() -> None:
    """Patch only the mutable specialist fields present in the request payload."""

    service = object.__new__(AdminSpecialistService)
    service.uow = Mock()
    service.logger = Mock()
    specialist = SimpleNamespace(
        full_name="Old Name",
        specialty="Old Specialty",
        bio="Old Bio",
        consultation_modes=["online"],
        city="Old City",
    )
    service._get_specialist_or_raise = Mock(return_value=specialist)
    payload = AdminSpecialistUpdateRequest(
        full_name="New Name",
        specialty=" New Specialty ",
        bio=" Updated bio ",
        consultation_modes=["in_person"],
        city=" Updated city ",
    )

    result = service.update_specialist(uuid4(), payload)

    assert result is specialist
    assert specialist.full_name == "New Name"
    assert specialist.specialty == "New Specialty"
    assert specialist.bio == "Updated bio"
    assert specialist.consultation_modes == ["in_person"]
    assert specialist.city == "Updated city"
    service.uow.commit.assert_called_once()
    service.uow.refresh.assert_called_once_with(specialist)


@pytest.mark.unit
def test_update_specialist_status_and_list_views_delegate_to_repository() -> None:
    """Update specialist status and map repository rows into admin response payloads."""

    service = object.__new__(AdminSpecialistService)
    service.uow = Mock()
    service.specialist_repository = Mock()
    service.logger = Mock()
    specialist = SimpleNamespace(id=uuid4(), status=SpecialistStatus.ACTIVE)
    service._get_specialist_or_raise = Mock(return_value=specialist)
    directory_row = SimpleNamespace(
        id=uuid4(),
        user_id=uuid4(),
        full_name="Dr. Listed",
        specialty="Psychology",
        bio=None,
        consultation_modes=["online"],
        city="Bucharest",
        status=SpecialistStatus.ACTIVE,
        email="doctor@example.com",
        user_is_active=True,
        average_rating=4.5,
        review_count=8,
    )
    service.specialist_repository.list_all_specialists.return_value = [directory_row]
    service.specialist_repository.list_all_specialists_paginated.return_value = [directory_row]
    service.specialist_repository.count_all_specialists.return_value = 1
    service.specialist_repository.get_specialist_directory_by_id.return_value = directory_row

    updated = service.update_specialist_status(
        specialist.id,
        AdminSpecialistStatusUpdateRequest(status=SpecialistStatus.INACTIVE),
    )
    listed = service.list_specialists()
    paginated, total = service.list_specialists_paginated(page=2, page_size=10)
    fetched = service.get_specialist(directory_row.id)

    assert updated.status == SpecialistStatus.INACTIVE
    service.uow.commit.assert_called_once()
    service.uow.refresh.assert_called_once_with(specialist)
    assert listed[0].id == directory_row.id
    assert paginated[0].id == directory_row.id
    assert total == 1
    assert fetched.id == directory_row.id
    service.specialist_repository.list_all_specialists_paginated.assert_called_once_with(page=2, page_size=10)


@pytest.mark.unit
def test_get_specialist_and_private_lookup_raise_when_missing() -> None:
    """Raise a domain error when an admin requests an unknown specialist."""

    service = object.__new__(AdminSpecialistService)
    service.db = Mock()
    service.specialist_repository = Mock()
    service.specialist_repository.get_specialist_directory_by_id.return_value = None
    service.db.get.return_value = None

    with pytest.raises(ValueError, match="Specialist not found."):
        service.get_specialist(uuid4())

    with pytest.raises(ValueError, match="Specialist not found."):
        service._get_specialist_or_raise(uuid4())

