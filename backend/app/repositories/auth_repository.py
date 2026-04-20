"""Repositories for user and authentication identity persistence."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

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

    def get_by_id(self, user_id) -> User | None:
        """Return a user by primary key."""

        return self.db.get(User, user_id)


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
