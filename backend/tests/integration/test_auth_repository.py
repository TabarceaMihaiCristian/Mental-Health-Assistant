"""Repository tests for authentication persistence helpers."""

from __future__ import annotations

from collections.abc import Callable

import pytest
from sqlalchemy.orm import Session

from app.models.enums import AuthProvider
from app.models.user import User
from app.repositories.auth_repository import AuthIdentityRepository, UserRepository


@pytest.mark.integration
def test_auth_identity_repository_matches_local_email_case_insensitively(
    db_session: Session,
    user_factory: Callable[..., User],
) -> None:
    """Look up local identities with case-insensitive email matching."""

    # Arrange
    user = user_factory(email="CaseSensitive@example.com")
    repository = AuthIdentityRepository(db_session)

    # Act
    identity = repository.get_local_identity_by_email("casesensitive@example.com")

    # Assert
    assert identity is not None
    assert identity.user_id == user.id
    assert identity.provider == AuthProvider.LOCAL


@pytest.mark.integration
def test_user_repository_get_by_id_returns_persisted_user(
    db_session: Session,
    user_factory: Callable[..., User],
) -> None:
    """Return a stored user by primary key."""

    # Arrange
    user = user_factory(email="lookup-user@example.com")
    repository = UserRepository(db_session)

    # Act
    found_user = repository.get_by_id(user.id)

    # Assert
    assert found_user is not None
    assert found_user.email == "lookup-user@example.com"
