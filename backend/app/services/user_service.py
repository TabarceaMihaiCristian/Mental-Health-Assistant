"""Account/profile service for authenticated users."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.db.unit_of_work import UnitOfWork
from app.models.user import User
from app.models.user_profile import UserProfile
from app.repositories.auth_repository import AuthIdentityRepository, UserRepository
from app.schemas.user import UserPasswordChangeRequest, UserProfileUpsertRequest


class LocalPasswordNotAvailableError(ValueError):
    """Raised when the user does not have a local password to update."""


class InvalidCurrentPasswordError(ValueError):
    """Raised when the supplied current password is incorrect."""


class UserService:
    """Manage authenticated user account/profile operations."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.uow = UnitOfWork(db)
        self.user_repository = UserRepository(db)
        self.identity_repository = AuthIdentityRepository(db)

    def get_current_user(self, user: User) -> User:
        refreshed = self.user_repository.get_by_id(user.id)
        if refreshed is None:
            raise ValueError("User not found.")
        return refreshed

    def update_profile(self, user: User, payload: UserProfileUpsertRequest) -> User:
        current_user = self.get_current_user(user)
        current_user.full_name = payload.full_name.strip()

        profile = current_user.profile
        if profile is None:
            profile = UserProfile(user=current_user)
            self.db.add(profile)

        profile.age_range = payload.age_range.strip() if payload.age_range else None
        profile.occupation = payload.occupation.strip() if payload.occupation else None
        profile.goals = payload.goals.strip() if payload.goals else None
        profile.preferred_activities = [item.strip() for item in payload.preferred_activities if item.strip()]
        profile.timezone = payload.timezone.strip()

        self.uow.commit()
        return self.get_current_user(current_user)

    def change_password(self, user: User, payload: UserPasswordChangeRequest) -> None:
        identity = self.identity_repository.get_local_identity_for_user(user.id)
        if identity is None or identity.password_hash is None:
            raise LocalPasswordNotAvailableError("Local password management is not available for this account.")

        if not verify_password(payload.current_password, identity.password_hash):
            raise InvalidCurrentPasswordError("Current password is incorrect.")

        identity.password_hash = hash_password(payload.new_password)
        self.uow.commit()
