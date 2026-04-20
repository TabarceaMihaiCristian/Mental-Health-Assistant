"""Authentication and user factory fixtures for backend tests."""

from __future__ import annotations

from collections.abc import Callable
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password
from app.models.auth_identity import AuthIdentity
from app.models.enums import AuthProvider, UserRole
from app.models.user import User

TEST_AUTH_SECRET = "StrongPass" + "123!"


@pytest.fixture()
def user_factory(db_session: Session) -> Callable[..., User]:
    """Return a factory that persists users with local-auth identities for tests."""

    def create_user(
        *,
        email: str | None = None,
        full_name: str = "Test User",
        raw_secret: str = TEST_AUTH_SECRET,
        role: UserRole = UserRole.USER,
        is_active: bool = True,
    ) -> User:
        """Create and flush one user plus its local authentication identity."""

        resolved_email = email or f"{uuid4().hex[:12]}@example.com"
        user = User(
            email=resolved_email,
            full_name=full_name,
            role=role,
            is_active=is_active,
        )
        auth_identity = AuthIdentity(
            user=user,
            provider=AuthProvider.LOCAL,
            provider_user_id=resolved_email,
            email=resolved_email,
            password_hash=hash_password(raw_secret),
            is_primary=True,
        )
        db_session.add(user)
        db_session.add(auth_identity)
        db_session.flush()
        return user

    return create_user


@pytest.fixture()
def auth_headers_factory() -> Callable[[User], dict[str, str]]:
    """Return a factory that builds bearer-auth headers for a persisted user."""

    def build_auth_headers(user: User) -> dict[str, str]:
        """Create authorization headers for one user using the application JWT helper."""

        token = create_access_token(str(user.id))
        return {"Authorization": f"Bearer {token}"}

    return build_auth_headers
