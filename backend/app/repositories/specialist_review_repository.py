"""Repositories for specialist review persistence and lookup."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.specialist_review import SpecialistReview


class SpecialistReviewRepository:
    """Database access helpers for specialist reviews."""

    def __init__(self, db: Session) -> None:
        """Bind the repository to one SQLAlchemy session."""

        self.db = db

    def add(self, review: SpecialistReview) -> SpecialistReview:
        """Persist a specialist review row."""

        self.db.add(review)
        self.db.flush()
        return review

    def get_by_specialist_and_user(
        self,
        specialist_id: UUID,
        user_id: UUID,
    ) -> SpecialistReview | None:
        """Return a user's review for a given specialist if it exists."""

        statement = select(SpecialistReview).where(
            SpecialistReview.specialist_id == specialist_id,
            SpecialistReview.user_id == user_id,
        )
        return self.db.scalar(statement)
