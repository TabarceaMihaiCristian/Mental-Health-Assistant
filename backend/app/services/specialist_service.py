"""Application service for the specialist directory."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.unit_of_work import UnitOfWork
from app.models.enums import SpecialistStatus
from app.models.specialist_review import SpecialistReview
from app.models.user import User
from app.repositories.specialist_review_repository import SpecialistReviewRepository
from app.repositories.specialist_repository import SpecialistDirectoryRow, SpecialistRepository
from app.schemas.specialist import SpecialistReviewUpsertRequest
from app.utils.logging import get_app_logger, log_event
from app.utils.validation import normalize_optional_comment


class SpecialistNotFoundError(ValueError):
    """Raised when the requested specialist cannot be found in the active directory."""


class SpecialistReviewAlreadyExistsError(ValueError):
    """Raised when trying to create a duplicate review for the same specialist and user."""


class SpecialistReviewNotFoundError(ValueError):
    """Raised when the current user has no review to update for a specialist."""


@dataclass(slots=True)
class SpecialistDirectoryItem:
    """Service-layer specialist directory item exposed to API schemas."""

    id: UUID
    full_name: str
    specialty: str
    bio: str | None
    consultation_modes: list[str]
    city: str | None
    status: SpecialistStatus
    average_rating: float | None
    review_count: int


class SpecialistService:
    """Read specialist directory data with aggregated review metadata."""

    def __init__(self, db: Session) -> None:
        """Bind specialist directory workflows to one SQLAlchemy session."""

        self.db = db
        self.uow = UnitOfWork(db)
        self.repository = SpecialistRepository(db)
        self.review_repository = SpecialistReviewRepository(db)
        self.logger = get_app_logger(__name__)

    def list_specialists(self) -> list[SpecialistDirectoryItem]:
        """Return all active specialists for directory browsing."""

        return [self._to_item(row) for row in self.repository.list_active_specialists()]

    def get_specialist(self, specialist_id: UUID) -> SpecialistDirectoryItem:
        """Return one active specialist from the directory."""

        specialist = self.repository.get_active_specialist_by_id(specialist_id)
        if specialist is None:
            raise SpecialistNotFoundError("Specialist not found.")
        return self._to_item(specialist)

    def create_review(
        self,
        user: User,
        specialist_id: UUID,
        payload: SpecialistReviewUpsertRequest,
    ) -> SpecialistReview:
        """Create a new review for an active specialist from the current user."""

        self.get_specialist(specialist_id)
        existing_review = self.review_repository.get_by_specialist_and_user(specialist_id, user.id)
        if existing_review is not None:
            raise SpecialistReviewAlreadyExistsError(
                "You have already reviewed this specialist."
            )

        review = SpecialistReview(
            specialist_id=specialist_id,
            user_id=user.id,
            rating=payload.rating,
            comment=normalize_optional_comment(payload.comment),
        )
        self.review_repository.add(review)
        self.uow.commit()
        self.uow.refresh(review)
        log_event(
            self.logger,
            "specialist.review.created",
            user_id=user.id,
            specialist_id=specialist_id,
            review_id=review.id,
            rating=review.rating,
        )
        return review

    def update_my_review(
        self,
        user: User,
        specialist_id: UUID,
        payload: SpecialistReviewUpsertRequest,
    ) -> SpecialistReview:
        """Update the current user's review for an active specialist."""

        self.get_specialist(specialist_id)
        review = self.review_repository.get_by_specialist_and_user(specialist_id, user.id)
        if review is None:
            raise SpecialistReviewNotFoundError("Review not found for this specialist.")

        review.rating = payload.rating
        review.comment = normalize_optional_comment(payload.comment)
        self.uow.commit()
        self.uow.refresh(review)
        log_event(
            self.logger,
            "specialist.review.updated",
            user_id=user.id,
            specialist_id=specialist_id,
            review_id=review.id,
            rating=review.rating,
        )
        return review

    def _to_item(self, row: SpecialistDirectoryRow) -> SpecialistDirectoryItem:
        """Map repository rows into service-layer directory items."""

        return SpecialistDirectoryItem(
            id=row.id,
            full_name=row.full_name,
            specialty=row.specialty,
            bio=row.bio,
            consultation_modes=row.consultation_modes,
            city=row.city,
            status=row.status,
            average_rating=row.average_rating,
            review_count=row.review_count,
        )
