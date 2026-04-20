"""Factory for selecting the correct authentication strategy by provider."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.enums import AuthProvider
from app.services.auth_strategies.auth_strategy import AuthStrategy
from app.services.auth_strategies.local_auth_strategy import LocalAuthStrategy


class AuthStrategyFactory:
    """Return provider-specific authentication strategy instances."""

    @staticmethod
    def get_strategy(provider: AuthProvider, db: Session) -> AuthStrategy:
        """Resolve the auth strategy for the requested provider."""

        if provider == AuthProvider.LOCAL:
            return LocalAuthStrategy(db)

        raise ValueError(f"Unsupported auth provider: {provider.value}")
