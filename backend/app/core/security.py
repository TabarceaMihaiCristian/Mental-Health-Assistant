"""Security helpers for password hashing and JWT token creation."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.repositories.auth_repository import UserRepository
from app.models.user import User


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)
DbSession = Annotated[Session, Depends(get_db)]
BearerCredentials = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]


def hash_password(password: str) -> str:
    """Hash a plain-text password for secure storage."""

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check whether a plain-text password matches a stored hash."""

    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    """Generate a signed JWT access token for the given subject."""

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.access_token_expire_minutes
    )
    payload = {
        "sub": subject,
        "exp": expire,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict[str, str]:
    """Decode a JWT access token and return its payload."""

    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])


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
