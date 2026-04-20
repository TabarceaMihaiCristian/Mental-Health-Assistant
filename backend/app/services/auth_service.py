"""Application service orchestrating authentication workflows."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.enums import AuthProvider
from app.models.user import User
from app.schemas.auth import AuthResponse, LocalLoginRequest, LocalRegisterRequest
from app.schemas.user import UserResponse
from app.services.auth_strategies.auth_strategy_factory import AuthStrategyFactory


class UnsupportedAuthProviderError(ValueError):
    """Raised when an auth provider does not have a registered strategy."""


class AuthService:
    """Coordinate provider strategies and JWT response generation."""

    def __init__(self, db: Session) -> None:
        """Bind authentication workflows to one SQLAlchemy session."""

        self.db = db

    def register_local_user(self, payload: LocalRegisterRequest) -> AuthResponse:
        """Register a local user and return an authenticated response."""

        strategy = self._get_strategy(AuthProvider.LOCAL)
        user = strategy.register(payload)
        return self._build_auth_response(user)

    def login_local_user(self, payload: LocalLoginRequest) -> AuthResponse:
        """Authenticate a local user and return an authenticated response."""

        strategy = self._get_strategy(AuthProvider.LOCAL)
        user = strategy.authenticate(payload)
        return self._build_auth_response(user)

    def _build_auth_response(self, user: User) -> AuthResponse:
        """Create the API auth response for a successfully authenticated user."""

        access_token = create_access_token(str(user.id))
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    def _get_strategy(self, provider: AuthProvider):
        """Resolve a provider-specific strategy or raise a domain error."""

        try:
            return AuthStrategyFactory.get_strategy(provider, self.db)
        except ValueError as exc:
            raise UnsupportedAuthProviderError(str(exc)) from exc
