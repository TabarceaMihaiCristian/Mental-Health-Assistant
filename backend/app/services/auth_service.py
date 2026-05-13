"""Application service orchestrating authentication workflows."""

from __future__ import annotations

from uuid import UUID

from jose import JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_password_reset_token,
    decode_password_reset_token,
    get_password_reset_fingerprint,
    hash_password,
)
from app.models.enums import AuthProvider
from app.models.user import User
from app.repositories.auth_repository import AuthIdentityRepository
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LocalLoginRequest,
    LocalRegisterRequest,
    PasswordResetResponse,
    ResetPasswordRequest,
)
from app.schemas.user import UserResponse
from app.services.auth_strategies.auth_strategy_factory import AuthStrategyFactory


PASSWORD_RESET_REQUEST_MESSAGE = (
    "If an account with that email exists, password reset instructions have been generated."
)
PASSWORD_RESET_SUCCESS_MESSAGE = "Your password has been updated. You can now sign in with the new password."
PASSWORD_RESET_TOKEN_ERROR_MESSAGE = "Invalid or expired password reset token."


class UnsupportedAuthProviderError(ValueError):
    """Raised when an auth provider does not have a registered strategy."""


class InvalidPasswordResetTokenError(ValueError):
    """Raised when a password reset token cannot be trusted anymore."""


class AuthService:
    """Coordinate provider strategies and JWT response generation."""

    def __init__(self, db: Session) -> None:
        """Bind authentication workflows to one SQLAlchemy session."""

        self.db = db
        self.identity_repository = AuthIdentityRepository(db)

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

    def request_password_reset(self, payload: ForgotPasswordRequest) -> ForgotPasswordResponse:
        """Return a generic password reset response and optionally expose a reset token."""

        normalized_email = payload.email.strip().lower()
        identity = self.identity_repository.get_local_identity_by_email(normalized_email)
        reset_token: str | None = None

        if identity is not None and identity.password_hash:
            reset_token = create_password_reset_token(
                str(identity.user_id),
                identity.password_hash,
                settings.password_reset_token_expire_minutes,
            )

        return ForgotPasswordResponse(
            message=PASSWORD_RESET_REQUEST_MESSAGE,
            reset_token=reset_token if self._should_expose_reset_token() else None,
        )

    def reset_password(self, payload: ResetPasswordRequest) -> PasswordResetResponse:
        """Validate a reset token and replace the user's local password hash."""

        try:
            token_payload = decode_password_reset_token(payload.token)
            user_id = UUID(token_payload["sub"])
        except (JWTError, ValueError) as exc:
            raise InvalidPasswordResetTokenError(PASSWORD_RESET_TOKEN_ERROR_MESSAGE) from exc

        identity = self.identity_repository.get_local_identity_for_user(user_id)
        if identity is None or identity.password_hash is None:
            raise InvalidPasswordResetTokenError(PASSWORD_RESET_TOKEN_ERROR_MESSAGE)

        expected_fingerprint = get_password_reset_fingerprint(identity.password_hash)
        if token_payload.get("phf") != expected_fingerprint:
            raise InvalidPasswordResetTokenError(PASSWORD_RESET_TOKEN_ERROR_MESSAGE)

        identity.password_hash = hash_password(payload.password)
        self.db.add(identity)
        self.db.commit()

        return PasswordResetResponse(message=PASSWORD_RESET_SUCCESS_MESSAGE)

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

    @staticmethod
    def _should_expose_reset_token() -> bool:
        """Expose reset tokens only in non-production environments without email delivery."""

        return settings.environment.lower() != "production"
