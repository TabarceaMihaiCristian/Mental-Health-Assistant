"""Pydantic schemas for authentication requests and responses."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserResponse


class LocalRegisterRequest(BaseModel):
    """Payload used to register a new account with email and password."""

    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class LocalLoginRequest(BaseModel):
    """Payload used to authenticate an existing local user."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class ForgotPasswordRequest(BaseModel):
    """Payload used to request a password reset token for a local account."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Payload used to confirm a new password with a reset token."""

    token: str = Field(min_length=1)
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    """JWT access token returned after a successful authentication flow."""

    access_token: str
    token_type: str = "bearer"


class AuthResponse(TokenResponse):
    """Authentication response containing both token data and user details."""

    user: UserResponse


class ForgotPasswordResponse(BaseModel):
    """Response returned after a password reset request is accepted."""

    message: str
    reset_token: str | None = None


class PasswordResetResponse(BaseModel):
    """Response returned after a password reset completes."""

    message: str
