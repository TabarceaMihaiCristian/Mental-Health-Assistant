"""Abstract authentication strategy contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.orm import Session

from app.db.unit_of_work import UnitOfWork
from app.models.user import User


class AuthStrategy(ABC):
    """Define the contract for provider-specific authentication strategies."""

    def __init__(self, db: Session) -> None:
        """Bind the strategy to one SQLAlchemy session."""

        self.db = db
        self.uow = UnitOfWork(db)

    @abstractmethod
    def register(self, payload: Any) -> User:
        """Register a user through the strategy-specific provider flow."""

    @abstractmethod
    def authenticate(self, payload: Any) -> User:
        """Authenticate a user through the strategy-specific provider flow."""
