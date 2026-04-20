"""Application service for admin-managed specialist onboarding."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.unit_of_work import UnitOfWork
from app.models.auth_identity import AuthIdentity
from app.models.enums import AuthProvider, SpecialistStatus, UserRole
from app.models.specialist import Specialist
from app.models.user import User
from app.repositories.auth_repository import AuthIdentityRepository, UserRepository
from app.repositories.specialist_repository import SpecialistRepository
from app.schemas.admin_specialist import (
    AdminSpecialistCreateRequest,
    AdminSpecialistResponse,
    AdminSpecialistStatusUpdateRequest,
    AdminSpecialistUpdateRequest,
)
from app.utils.logging import get_app_logger, log_event
from app.utils.validation import normalize_email, normalize_full_name, normalize_optional_comment


class SpecialistOnboardingConflictError(ValueError):
    """Raised when a specialist onboarding request conflicts with existing auth data."""


class AdminSpecialistService:
    """Create and update specialist profiles on behalf of admins."""

    def __init__(self, db: Session) -> None:
        """Bind onboarding workflows to one SQLAlchemy session."""

        self.db = db
        self.uow = UnitOfWork(db)
        self.user_repository = UserRepository(db)
        self.identity_repository = AuthIdentityRepository(db)
        self.specialist_repository = SpecialistRepository(db)
        self.logger = get_app_logger(__name__)

    def create_specialist(self, payload: AdminSpecialistCreateRequest) -> Specialist:
        """Create a specialist user, auth identity, and specialist profile."""

        normalized_email = normalize_email(payload.email)
        existing_identity = self.identity_repository.get_local_identity_by_email(normalized_email)
        if existing_identity is not None:
            raise SpecialistOnboardingConflictError("A user with this email already exists.")

        user = User(
            email=normalized_email,
            full_name=normalize_full_name(payload.full_name),
            role=UserRole.SPECIALIST,
            is_active=True,
        )
        self.user_repository.add(user)

        identity = AuthIdentity(
            user_id=user.id,
            provider=AuthProvider.LOCAL,
            provider_user_id=normalized_email,
            email=normalized_email,
            password_hash=hash_password(payload.password),
            is_primary=True,
        )
        self.identity_repository.add(identity)

        specialist = Specialist(
            user_id=user.id,
            full_name=normalize_full_name(payload.full_name),
            specialty=payload.specialty.strip(),
            bio=normalize_optional_comment(payload.bio),
            consultation_modes=payload.consultation_modes,
            city=normalize_optional_comment(payload.city),
            status=SpecialistStatus.ACTIVE,
        )
        self.specialist_repository.add(specialist)
        self.uow.commit()
        self.uow.refresh(specialist)
        log_event(
            self.logger,
            "admin.specialist.created",
            user_id=user.id,
            specialist_id=specialist.id,
            email=normalized_email,
        )
        return specialist

    def update_specialist(
        self,
        specialist_id: UUID,
        payload: AdminSpecialistUpdateRequest,
    ) -> Specialist:
        """Update mutable specialist profile fields."""

        specialist = self._get_specialist_or_raise(specialist_id)
        if payload.full_name is not None:
            specialist.full_name = normalize_full_name(payload.full_name)
        if payload.specialty is not None:
            specialist.specialty = payload.specialty.strip()
        if payload.bio is not None:
            specialist.bio = normalize_optional_comment(payload.bio)
        if payload.consultation_modes is not None:
            specialist.consultation_modes = payload.consultation_modes
        if payload.city is not None:
            specialist.city = normalize_optional_comment(payload.city)
        self.uow.commit()
        self.uow.refresh(specialist)
        return specialist

    def update_specialist_status(
        self,
        specialist_id: UUID,
        payload: AdminSpecialistStatusUpdateRequest,
    ) -> Specialist:
        """Update a specialist's directory status."""

        specialist = self._get_specialist_or_raise(specialist_id)
        specialist.status = payload.status
        self.uow.commit()
        self.uow.refresh(specialist)
        return specialist

    def list_specialists(self) -> list[AdminSpecialistResponse]:
        """Return all specialists for admin oversight views."""

        return [
            AdminSpecialistResponse.model_validate(item)
            for item in self.specialist_repository.list_all_specialists()
        ]

    def list_specialists_paginated(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[AdminSpecialistResponse], int]:
        """Return paginated specialists and the total count for admin oversight views."""

        specialists = [
            AdminSpecialistResponse.model_validate(item)
            for item in self.specialist_repository.list_all_specialists_paginated(
                page=page,
                page_size=page_size,
            )
        ]
        total = self.specialist_repository.count_all_specialists()
        return specialists, total

    def get_specialist(self, specialist_id: UUID) -> AdminSpecialistResponse:
        """Return one specialist for admin oversight views."""

        specialist = self.specialist_repository.get_specialist_directory_by_id(specialist_id)
        if specialist is None:
            raise ValueError("Specialist not found.")
        return AdminSpecialistResponse.model_validate(specialist)

    def _get_specialist_or_raise(self, specialist_id: UUID) -> Specialist:
        """Return a specialist by id or raise a domain error."""

        specialist = self.db.get(Specialist, specialist_id)
        if specialist is None:
            raise ValueError("Specialist not found.")
        return specialist
