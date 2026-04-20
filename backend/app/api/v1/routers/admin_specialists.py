"""Admin endpoints for specialist onboarding and profile management."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.authorization import require_admin_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.admin_specialist import (
    AdminSpecialistCreateRequest,
    AdminSpecialistPageResponse,
    AdminSpecialistResponse,
    AdminSpecialistStatusUpdateRequest,
    AdminSpecialistUpdateRequest,
)
from app.services.admin_specialist_service import (
    AdminSpecialistService,
    SpecialistOnboardingConflictError,
)

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]
AdminUser = Annotated[User, Depends(require_admin_user)]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_specialist(
    payload: AdminSpecialistCreateRequest,
    _: AdminUser,
    db: DbSession,
) -> AdminSpecialistResponse:
    """Create a specialist user account and linked specialist directory profile."""

    service = AdminSpecialistService(db)
    try:
        specialist = service.create_specialist(payload)
    except SpecialistOnboardingConflictError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return AdminSpecialistResponse.model_validate(specialist)


@router.get("")
def list_specialists(
    _: AdminUser,
    db: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 50,
) -> AdminSpecialistPageResponse:
    """List all specialists for admin oversight views."""

    specialists, total = AdminSpecialistService(db).list_specialists_paginated(
        page=page,
        page_size=page_size,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return AdminSpecialistPageResponse(
        items=specialists,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


@router.get("/{specialist_id}")
def get_specialist(
    specialist_id: UUID,
    _: AdminUser,
    db: DbSession,
) -> AdminSpecialistResponse:
    """Return one specialist for admin oversight views."""

    try:
        return AdminSpecialistService(db).get_specialist(specialist_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{specialist_id}")
def update_specialist(
    specialist_id: UUID,
    payload: AdminSpecialistUpdateRequest,
    _: AdminUser,
    db: DbSession,
) -> AdminSpecialistResponse:
    """Update specialist profile details."""

    try:
        specialist = AdminSpecialistService(db).update_specialist(specialist_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return AdminSpecialistResponse.model_validate(specialist)


@router.patch("/{specialist_id}/status")
def update_specialist_status(
    specialist_id: UUID,
    payload: AdminSpecialistStatusUpdateRequest,
    _: AdminUser,
    db: DbSession,
) -> AdminSpecialistResponse:
    """Update specialist directory status."""

    try:
        specialist = AdminSpecialistService(db).update_specialist_status(specialist_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return AdminSpecialistResponse.model_validate(specialist)
