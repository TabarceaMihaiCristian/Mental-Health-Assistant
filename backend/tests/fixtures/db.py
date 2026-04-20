"""Database and API client fixtures for backend tests."""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import Session, sessionmaker

from app import models as _models  # noqa: F401
from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def _build_test_session_factory(bind: Connection) -> sessionmaker[Session]:
    """Return a SQLAlchemy session factory bound to one test connection."""

    return sessionmaker(
        bind=bind,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )


def _reset_public_schema(engine: Engine) -> None:
    """Rebuild the public PostgreSQL schema so enums and tables reset cleanly."""

    with engine.begin() as connection:
        connection.exec_driver_sql("DROP SCHEMA IF EXISTS public CASCADE")
        connection.exec_driver_sql("CREATE SCHEMA public")
        connection.exec_driver_sql("GRANT ALL ON SCHEMA public TO postgres")
        connection.exec_driver_sql("GRANT ALL ON SCHEMA public TO public")


@pytest.fixture(scope="session")
def test_database_url() -> str:
    """Return the required database URL used by integration and end-to-end tests."""

    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "TEST_DATABASE_URL must be set for the backend test suite."
        )
    return database_url


@pytest.fixture(scope="session")
def test_engine(test_database_url: str) -> Generator[Engine, None, None]:
    """Create the shared SQLAlchemy engine used by database-backed tests."""

    engine = create_engine(test_database_url, pool_pre_ping=True)
    try:
        yield engine
    finally:
        _reset_public_schema(engine)
        engine.dispose()


@pytest.fixture()
def db_session(test_engine: Engine) -> Generator[Session, None, None]:
    """Yield a database session against a schema rebuilt for one test only."""

    _reset_public_schema(test_engine)
    Base.metadata.create_all(bind=test_engine)
    connection = test_engine.connect()
    session = _build_test_session_factory(connection)()
    try:
        yield session
    finally:
        session.close()
        connection.close()


@pytest.fixture()
def app(db_session: Session) -> Generator[FastAPI, None, None]:
    """Yield the FastAPI app with the database dependency overridden for tests."""

    from app.main import app as fastapi_app

    original_scheduler_enabled = settings.scheduler_enabled
    settings.scheduler_enabled = False

    def override_get_db() -> Generator[Session, None, None]:
        """Provide the per-test SQLAlchemy session to request handlers."""

        yield db_session

    fastapi_app.dependency_overrides[get_db] = override_get_db
    try:
        yield fastapi_app
    finally:
        fastapi_app.dependency_overrides.clear()
        settings.scheduler_enabled = original_scheduler_enabled


@pytest.fixture()
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    """Yield a synchronous API client bound to the test application."""

    with TestClient(app) as test_client:
        yield test_client
