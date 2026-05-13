"""Repositories for user and authentication identity persistence."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.auth_identity import AuthIdentity
from app.models.enums import AuthProvider
from app.models.user import User


class UserRepository:
    """Database access helpers for user records."""

    def __init__(self, db: Session) -> None:
        """Bind the repository to one SQLAlchemy session."""

        self.db = db

    def add(self, user: User) -> User:
        """Persist a user."""

        self.db.add(user)
        self.db.flush()
        return user

    def get_by_id(self, user_id: UUID) -> User | None:
        """Return a user by primary key with profile and identities loaded."""

        statement = (
            select(User)
            .options(
                selectinload(User.profile),
                selectinload(User.auth_identities),
            )
            .where(User.id == user_id)
        )
        return self.db.scalar(statement)


class AuthIdentityRepository:
    """Database access helpers for authentication identities."""

    def __init__(self, db: Session) -> None:
        """Bind the repository to one SQLAlchemy session."""

        self.db = db

    def add(self, identity: AuthIdentity) -> AuthIdentity:
        """Persist an auth identity."""

        self.db.add(identity)
        self.db.flush()
        return identity

    def get_local_identity_by_email(self, email: str) -> AuthIdentity | None:
        """Look up a local auth identity by normalized email."""

        statement = select(AuthIdentity).where(
            AuthIdentity.provider == AuthProvider.LOCAL,
            func.lower(AuthIdentity.email) == email,
        )
        return self.db.scalar(statement)

    def get_local_identity_for_user(self, user_id: UUID) -> AuthIdentity | None:
        """Return the primary local auth identity for a user, if one exists."""

        statement = (
            select(AuthIdentity)
            .where(
                AuthIdentity.user_id == user_id,
                AuthIdentity.provider == AuthProvider.LOCAL,
            )
            .order_by(AuthIdentity.is_primary.desc(), AuthIdentity.created_at.asc())
        )
        return self.db.scalar(statement)
