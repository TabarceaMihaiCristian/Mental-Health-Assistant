"""Security helpers for password hashing and JWT token creation."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.repositories.auth_repository import UserRepository


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)
DbSession = Annotated[Session, Depends(get_db)]
BearerCredentials = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]
PASSWORD_RESET_TOKEN_PURPOSE = "password_reset"


def hash_password(password: str) -> str:
    """Hash a plain-text password for secure storage."""

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check whether a plain-text password matches a stored hash."""

    return pwd_context.verify(plain_password, hashed_password)


def get_password_reset_fingerprint(password_hash: str | None) -> str:
    """Create a stable fingerprint from the stored password hash."""

    return sha256((password_hash or "").encode("utf-8")).hexdigest()


def _encode_signed_token(payload: dict[str, object], expires_minutes: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    token_payload = {**payload, "exp": expire}
    return jwt.encode(token_payload, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    """Generate a signed JWT access token for the given subject."""

    return _encode_signed_token(
        {"sub": subject},
        expires_minutes or settings.access_token_expire_minutes,
    )


def create_password_reset_token(
    subject: str,
    password_hash: str | None,
    expires_minutes: int | None = None,
) -> str:
    """Generate a signed password reset token bound to the current password hash."""

    return _encode_signed_token(
        {
            "sub": subject,
            "purpose": PASSWORD_RESET_TOKEN_PURPOSE,
            "phf": get_password_reset_fingerprint(password_hash),
        },
        expires_minutes or settings.password_reset_token_expire_minutes,
    )


def decode_access_token(token: str) -> dict[str, str]:
    """Decode a JWT access token and return its payload."""

    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])


def decode_password_reset_token(token: str) -> dict[str, str]:
    """Decode a password reset token and validate its purpose payload."""

    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    if payload.get("purpose") != PASSWORD_RESET_TOKEN_PURPOSE:
        raise JWTError("Invalid token purpose")
    if payload.get("sub") is None or payload.get("phf") is None:
        raise JWTError("Incomplete password reset token")
    return payload


def get_current_user(credentials: BearerCredentials, db: DbSession) -> User:
    """Resolve the authenticated user from a bearer token."""

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = decode_access_token(credentials.credentials)
        subject = payload.get("sub")
        if subject is None:
            raise ValueError("Missing token subject")
        user_id = UUID(subject)
    except (JWTError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from exc

    user = UserRepository(db).get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user
