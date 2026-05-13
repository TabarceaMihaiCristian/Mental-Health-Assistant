"""User account and profile API endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserPasswordChangeRequest, UserProfileUpsertRequest, UserResponse
from app.services.user_service import (
    InvalidCurrentPasswordError,
    LocalPasswordNotAvailableError,
    UserService,
)


router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/me")
def get_my_account(current_user: CurrentUser, db: DbSession) -> UserResponse:
    """Return the authenticated user's account and profile data."""

    user = UserService(db).get_current_user(current_user)
    return UserResponse.model_validate(user)


@router.put("/me")
def update_my_profile(
    payload: UserProfileUpsertRequest,
    current_user: CurrentUser,
    db: DbSession,
) -> UserResponse:
    """Update the authenticated user's account/profile fields."""

    user = UserService(db).update_profile(current_user, payload)
    return UserResponse.model_validate(user)


@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_my_password(
    payload: UserPasswordChangeRequest,
    current_user: CurrentUser,
    db: DbSession,
) -> None:
    """Change the authenticated user's local password."""

    service = UserService(db)
    try:
        service.change_password(current_user, payload)
    except LocalPasswordNotAvailableError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except InvalidCurrentPasswordError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
