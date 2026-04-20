"""Repository tests for specialist review lookups."""

from __future__ import annotations

from collections.abc import Callable

import pytest
from sqlalchemy.orm import Session

from app.models.specialist_review import SpecialistReview
from app.models.specialist import Specialist
from app.models.user import User
from app.repositories.specialist_review_repository import SpecialistReviewRepository


@pytest.mark.integration
def test_specialist_review_repository_scopes_by_specialist_and_user(
    db_session: Session,
    user_factory: Callable[..., User],
    specialist_factory: Callable[..., Specialist],
) -> None:
    """Return only the review that matches both specialist and reviewer ids."""

    # Arrange
    reviewer = user_factory()
    other_reviewer = user_factory()
    specialist = specialist_factory(full_name="Dr. Review Repo")
    other_specialist = specialist_factory(full_name="Dr. Review Elsewhere")
    review = SpecialistReview(
        specialist_id=specialist.id,
        user_id=reviewer.id,
        rating=5,
        comment="Excellent support.",
    )
    db_session.add_all(
        [
            review,
            SpecialistReview(
                specialist_id=specialist.id,
                user_id=other_reviewer.id,
                rating=3,
                comment="Different reviewer.",
            ),
            SpecialistReview(
                specialist_id=other_specialist.id,
                user_id=reviewer.id,
                rating=4,
                comment="Different specialist.",
            ),
        ]
    )
    db_session.flush()
    repository = SpecialistReviewRepository(db_session)

    # Act
    matched = repository.get_by_specialist_and_user(specialist.id, reviewer.id)
    missing = repository.get_by_specialist_and_user(other_specialist.id, other_reviewer.id)

    # Assert
    assert matched is not None
    assert matched.id == review.id
    assert missing is None
