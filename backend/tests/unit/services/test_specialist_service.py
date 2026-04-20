"""Unit tests for specialist directory review workflows."""

from __future__ import annotations

from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.models.enums import UserRole
from app.models.user import User
from app.schemas.specialist import SpecialistReviewUpsertRequest
from app.services.specialist_service import (
    SpecialistReviewAlreadyExistsError,
    SpecialistReviewNotFoundError,
    SpecialistService,
)


def _user() -> User:
    user = User(email=f"{uuid4().hex[:12]}@example.com", full_name="Specialist Review User", role=UserRole.USER)
    user.id = uuid4()
    return user


@pytest.mark.unit
def test_create_review_rejects_duplicate_reviews() -> None:
    """Reject a second review from the same user for the same specialist."""

    service = object.__new__(SpecialistService)
    service.uow = Mock()
    service.repository = Mock()
    service.review_repository = Mock()
    service.logger = Mock()
    user = _user()
    specialist_id = uuid4()
    payload = SpecialistReviewUpsertRequest(rating=5, comment="Very helpful.")
    service.get_specialist = Mock()
    service.review_repository.get_by_specialist_and_user.return_value = object()

    with pytest.raises(
        SpecialistReviewAlreadyExistsError,
        match="You have already reviewed this specialist.",
    ):
        service.create_review(user, specialist_id, payload)


@pytest.mark.unit
def test_update_my_review_rejects_missing_review() -> None:
    """Reject review updates when the current user has no existing review."""

    service = object.__new__(SpecialistService)
    service.uow = Mock()
    service.repository = Mock()
    service.review_repository = Mock()
    service.logger = Mock()
    user = _user()
    specialist_id = uuid4()
    payload = SpecialistReviewUpsertRequest(rating=3, comment="Updated.")
    service.get_specialist = Mock()
    service.review_repository.get_by_specialist_and_user.return_value = None

    with pytest.raises(
        SpecialistReviewNotFoundError,
        match="Review not found for this specialist.",
    ):
        service.update_my_review(user, specialist_id, payload)
