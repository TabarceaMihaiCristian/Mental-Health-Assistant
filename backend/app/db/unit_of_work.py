"""Small unit-of-work helpers around the SQLAlchemy session."""

from __future__ import annotations

from sqlalchemy.orm import Session


class UnitOfWork:
    """Centralize commit, rollback, and refresh operations for a session."""

    def __init__(self, db: Session) -> None:
        """Bind the helper to one SQLAlchemy session."""

        self.db = db

    def commit(self) -> None:
        """Commit the current transaction."""

        self.db.commit()

    def rollback(self) -> None:
        """Roll back the current transaction."""

        self.db.rollback()

    def refresh(self, instance: object) -> None:
        """Refresh one ORM instance from the database."""

        self.db.refresh(instance)
