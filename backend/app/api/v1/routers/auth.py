"""Authentication API endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
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
from app.services.auth_service import (
    AuthService,
    InvalidPasswordResetTokenError,
    UnsupportedAuthProviderError,
)
from app.services.auth_strategies.local_auth_strategy import (
    IdentityAlreadyExistsError,
    InactiveUserError,
    InvalidCredentialsError,
)


router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_local_user(payload: LocalRegisterRequest, db: DbSession) -> AuthResponse:
    """Register a user with local email/password authentication."""

    service = AuthService(db)
    try:
        return service.register_local_user(payload)
    except IdentityAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except UnsupportedAuthProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post("/login")
def login_local_user(payload: LocalLoginRequest, db: DbSession) -> AuthResponse:
    """Authenticate a user through the local email/password flow."""

    service = AuthService(db)
    try:
        return service.login_local_user(payload)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    except InactiveUserError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except UnsupportedAuthProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post("/forgot-password")
def request_password_reset(payload: ForgotPasswordRequest, db: DbSession) -> ForgotPasswordResponse:
    """Accept a password reset request and return a generic response."""

    return AuthService(db).request_password_reset(payload)


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: DbSession) -> PasswordResetResponse:
    """Validate a password reset token and replace the local password hash."""

    try:
        return AuthService(db).reset_password(payload)
    except InvalidPasswordResetTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/me")
def get_current_authenticated_user(current_user: CurrentUser) -> UserResponse:
    """Return the currently authenticated user's public profile."""

    return UserResponse.model_validate(current_user)
