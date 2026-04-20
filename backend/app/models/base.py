"""Shared SQLAlchemy base classes and mixins used by ORM models."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base declarative class for all ORM models."""


def utc_now() -> datetime:
    """Return the current UTC timestamp for default ORM values."""

    return datetime.now(timezone.utc)


class CreatedAtMixin:
    """Mixin that adds a creation timestamp to immutable records."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )


class TimestampMixin(CreatedAtMixin):
    """Mixin that adds creation and update timestamps to mutable records."""

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
