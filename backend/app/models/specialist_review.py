"""ORM model for user reviews left on specialist profiles."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, SmallInteger, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.specialist import Specialist
    from app.models.user import User


class SpecialistReview(Base, TimestampMixin):
    """Represent a single user's rating and optional comment for a specialist."""

    __tablename__ = "specialist_reviews"
    __table_args__ = (
        UniqueConstraint("specialist_id", "user_id", name="uq_specialist_reviews_specialist_user"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_specialist_reviews_rating_range"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    specialist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("specialists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)

    specialist: Mapped[Specialist] = relationship("Specialist", back_populates="reviews")
    user: Mapped[User] = relationship("User", back_populates="specialist_reviews")
