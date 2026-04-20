"""Repositories for specialist directory queries and rating aggregation."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.enums import SpecialistStatus
from app.models.specialist import Specialist


@dataclass(slots=True)
class SpecialistDirectoryRow:
    """Flattened specialist directory record with aggregated review metadata."""

    id: UUID
    full_name: str
    specialty: str
    bio: str | None
    consultation_modes: list[str]
    city: str | None
    status: SpecialistStatus
    average_rating: float | None
    review_count: int
    user_id: UUID | None = None
    email: str | None = None
    user_is_active: bool | None = None


class SpecialistRepository:
    """Database access helpers for specialist directory views."""

    def __init__(self, db: Session) -> None:
        """Bind the repository to one SQLAlchemy session."""

        self.db = db

    def list_active_specialists(self) -> list[SpecialistDirectoryRow]:
        """Return active specialists with aggregated ratings and review counts."""

        statement = self._base_directory_statement().where(
            Specialist.status == SpecialistStatus.ACTIVE
        )
        specialists = list(self.db.scalars(statement).all())
        return [self._to_directory_row(specialist) for specialist in specialists]

    def list_all_specialists(self) -> list[SpecialistDirectoryRow]:
        """Return all specialists with aggregated ratings and linked-user metadata."""

        specialists = list(self.db.scalars(self._base_directory_statement()).all())
        return [self._to_directory_row(specialist) for specialist in specialists]

    def list_all_specialists_paginated(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
    ) -> list[SpecialistDirectoryRow]:
        """Return paginated specialists with aggregated ratings and linked-user metadata."""

        offset = (page - 1) * page_size
        statement = self._base_directory_statement().offset(offset).limit(page_size)
        specialists = list(self.db.scalars(statement).all())
        return [self._to_directory_row(specialist) for specialist in specialists]

    def count_all_specialists(self) -> int:
        """Return the total specialist count for admin oversight views."""

        statement = select(func.count(Specialist.id))
        count = self.db.scalar(statement)
        return 0 if count is None else int(count)

    def get_specialist_directory_by_id(
        self,
        specialist_id: UUID,
    ) -> SpecialistDirectoryRow | None:
        """Return one specialist regardless of status with directory metadata."""

        statement = self._base_directory_statement().where(Specialist.id == specialist_id)
        specialist = self.db.scalar(statement)
        return None if specialist is None else self._to_directory_row(specialist)

    def get_active_specialist_by_id(self, specialist_id: UUID) -> SpecialistDirectoryRow | None:
        """Return one active specialist with aggregated ratings and review counts."""

        statement = self._base_directory_statement().where(
            Specialist.id == specialist_id,
            Specialist.status == SpecialistStatus.ACTIVE,
        )
        specialist = self.db.scalar(statement)
        return None if specialist is None else self._to_directory_row(specialist)

    def get_by_user_id(self, user_id: UUID) -> Specialist | None:
        """Return the specialist profile linked to a given specialist user."""

        statement = select(Specialist).where(Specialist.user_id == user_id)
        return self.db.scalar(statement)

    def get_by_id(self, specialist_id: UUID) -> Specialist | None:
        """Return a specialist profile by primary key regardless of status."""

        statement = select(Specialist).where(Specialist.id == specialist_id)
        return self.db.scalar(statement)

    def add(self, specialist: Specialist) -> Specialist:
        """Persist a specialist profile row."""

        self.db.add(specialist)
        self.db.flush()
        return specialist

    def _base_directory_statement(self):
        """Build the shared ORM select used for directory aggregation."""

        return (
            select(Specialist)
            .options(selectinload(Specialist.reviews), selectinload(Specialist.user))
            .order_by(Specialist.full_name.asc())
        )

    def _to_directory_row(self, specialist: Specialist) -> SpecialistDirectoryRow:
        """Map a specialist ORM entity into a typed directory record."""

        ratings = [review.rating for review in specialist.reviews]
        average_rating = round(sum(ratings) / len(ratings), 2) if ratings else None

        return SpecialistDirectoryRow(
            id=specialist.id,
            full_name=specialist.full_name,
            specialty=specialist.specialty,
            bio=specialist.bio,
            consultation_modes=specialist.consultation_modes,
            city=specialist.city,
            status=specialist.status,
            average_rating=average_rating,
            review_count=len(ratings),
            user_id=specialist.user_id,
            email=None if specialist.user is None else specialist.user.email,
            user_is_active=None if specialist.user is None else specialist.user.is_active,
        )
