"""Role-based authorization dependencies for protected routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user
from app.models.enums import UserRole
from app.models.user import User

CurrentUser = Annotated[User, Depends(get_current_user)]


def require_admin_user(current_user: CurrentUser) -> User:
    """Ensure the authenticated user has admin privileges."""

    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges are required.",
        )
    return current_user


def require_specialist_user(current_user: CurrentUser) -> User:
    """Ensure the authenticated user has specialist privileges."""

    if current_user.role != UserRole.SPECIALIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Specialist privileges are required.",
        )
    return current_user
