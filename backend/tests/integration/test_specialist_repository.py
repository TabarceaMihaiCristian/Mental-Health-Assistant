"""Repository tests for specialist directory aggregation."""

from __future__ import annotations

from collections.abc import Callable

import pytest
from sqlalchemy.orm import Session

from app.models.enums import SpecialistStatus
from app.models.specialist import Specialist
from app.models.specialist_review import SpecialistReview
from app.models.user import User
from app.repositories.specialist_repository import SpecialistRepository


@pytest.mark.integration
def test_specialist_repository_filters_active_and_aggregates_reviews(
    db_session: Session,
    user_factory: Callable[..., User],
    specialist_factory: Callable[..., Specialist],
) -> None:
    """Return only active specialists in the public directory with computed rating metadata."""

    # Arrange
    reviewer = user_factory()
    active_specialist = specialist_factory(full_name="Dr. Active", status=SpecialistStatus.ACTIVE)
    inactive_specialist = specialist_factory(full_name="Dr. Inactive", status=SpecialistStatus.INACTIVE)
    db_session.add_all(
        [
            SpecialistReview(
                specialist_id=active_specialist.id,
                user_id=reviewer.id,
                rating=4,
                comment="Helpful.",
            ),
        ]
    )
    db_session.flush()
    repository = SpecialistRepository(db_session)

    # Act
    active_rows = repository.list_active_specialists()
    all_rows = repository.list_all_specialists()
    paginated_rows = repository.list_all_specialists_paginated(page=1, page_size=1)
    directory_entry = repository.get_specialist_directory_by_id(active_specialist.id)

    # Assert
    assert [item.id for item in active_rows] == [active_specialist.id]
    active_row = active_rows[0]
    assert active_row.average_rating == pytest.approx(4.0)
    assert active_row.review_count == 1
    assert {item.id for item in all_rows} == {active_specialist.id, inactive_specialist.id}
    assert len(paginated_rows) == 1
    assert repository.count_all_specialists() == 2
    assert directory_entry is not None
    assert active_specialist.user is not None
    assert directory_entry.email == active_specialist.user.email
    assert repository.get_active_specialist_by_id(inactive_specialist.id) is None


@pytest.mark.integration
def test_specialist_repository_getters_return_raw_profiles(
    db_session: Session,
    specialist_factory: Callable[..., Specialist],
) -> None:
    """Return linked specialist profiles by user id and primary key."""

    # Arrange
    specialist = specialist_factory(full_name="Dr. Raw Getter")
    repository = SpecialistRepository(db_session)

    # Act
    assert specialist.user_id is not None
    by_user = repository.get_by_user_id(specialist.user_id)
    by_id = repository.get_by_id(specialist.id)

    # Assert
    assert by_user is not None
    assert by_user.id == specialist.id
    assert by_id is not None
    assert by_id.user_id == specialist.user_id
