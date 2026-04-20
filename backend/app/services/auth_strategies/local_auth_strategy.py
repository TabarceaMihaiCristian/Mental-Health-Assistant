"""Local email/password authentication strategy."""

from __future__ import annotations

from app.core.security import hash_password, verify_password
from app.models.auth_identity import AuthIdentity
from app.models.enums import AuthProvider
from app.models.user import User
from app.repositories.auth_repository import AuthIdentityRepository, UserRepository
from app.schemas.auth import LocalLoginRequest, LocalRegisterRequest
from app.services.auth_strategies.auth_strategy import AuthStrategy
from app.utils.logging import get_app_logger, log_event, mask_email, mask_uuid
from app.utils.validation import normalize_email, normalize_full_name


class IdentityAlreadyExistsError(ValueError):
    """Raised when a local auth identity already exists for the email."""


class InvalidCredentialsError(ValueError):
    """Raised when the provided authentication credentials are invalid."""


class InactiveUserError(ValueError):
    """Raised when an inactive account attempts to authenticate."""


class LocalAuthStrategy(AuthStrategy):
    """Handle registration and authentication for local email/password accounts."""

    def __init__(self, db) -> None:
        """Initialize the strategy with repository dependencies."""

        super().__init__(db)
        self.user_repository = UserRepository(db)
        self.identity_repository = AuthIdentityRepository(db)
        self.logger = get_app_logger(__name__)

    def register(self, payload: LocalRegisterRequest) -> User:
        """Create a user and its linked local auth identity."""

        normalized_email = normalize_email(payload.email)
        existing_identity = self.identity_repository.get_local_identity_by_email(normalized_email)
        if existing_identity is not None:
            log_event(
                self.logger,
                "auth.register.duplicate_email",
                email=mask_email(normalized_email),
            )
            raise IdentityAlreadyExistsError("A user with this email already exists.")

        user = User(
            email=normalized_email,
            full_name=normalize_full_name(payload.full_name),
        )
        auth_identity = AuthIdentity(
            user=user,
            provider=AuthProvider.LOCAL,
            provider_user_id=normalized_email,
            email=normalized_email,
            password_hash=hash_password(payload.password),
            is_primary=True,
        )

        self.user_repository.add(user)
        self.identity_repository.add(auth_identity)
        self.uow.commit()
        self.uow.refresh(user)
        log_event(
            self.logger,
            "auth.register.success",
            user_id=mask_uuid(user.id),
            email=mask_email(user.email),
        )
        return user

    def authenticate(self, payload: LocalLoginRequest) -> User:
        """Validate local credentials and return the linked active user."""

        normalized_email = normalize_email(payload.email)
        auth_identity = self.identity_repository.get_local_identity_by_email(normalized_email)
        if auth_identity is None or auth_identity.password_hash is None:
            log_event(
                self.logger,
                "auth.login.invalid_credentials",
                email=mask_email(normalized_email),
            )
            raise InvalidCredentialsError("Invalid email or password.")

        if not verify_password(payload.password, auth_identity.password_hash):
            log_event(
                self.logger,
                "auth.login.invalid_credentials",
                email=mask_email(normalized_email),
            )
            raise InvalidCredentialsError("Invalid email or password.")

        user = auth_identity.user
        if not user.is_active:
            log_event(
                self.logger,
                "auth.login.inactive_user",
                user_id=mask_uuid(user.id),
                email=mask_email(user.email),
            )
            raise InactiveUserError("User account is inactive.")

        log_event(
            self.logger,
            "auth.login.success",
            user_id=mask_uuid(user.id),
            email=mask_email(user.email),
        )
        return user
