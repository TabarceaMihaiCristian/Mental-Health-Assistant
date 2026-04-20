"""Integration tests for specialist review endpoints."""

from __future__ import annotations

from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient

from app.models.specialist import Specialist
from app.models.user import User


@pytest.mark.integration
def test_user_can_create_and_update_specialist_review(
    client: TestClient,
    user_factory: Callable[..., User],
    specialist_factory: Callable[..., Specialist],
    auth_headers_factory,
) -> None:
    """Allow an authenticated user to create and later update their review."""

    # Arrange
    user = user_factory()
    specialist = specialist_factory(full_name="Dr. Reviewed")
    headers = auth_headers_factory(user)

    # Act
    create_response = client.post(
        f"/api/v1/specialists/{specialist.id}/reviews",
        json={"rating": 5, "comment": "Great support."},
        headers=headers,
    )
    update_response = client.put(
        f"/api/v1/specialists/{specialist.id}/reviews/me",
        json={"rating": 4, "comment": "Still very helpful."},
        headers=headers,
    )

    # Assert
    assert create_response.status_code == 201
    assert create_response.json()["rating"] == 5
    assert update_response.status_code == 200
    assert update_response.json()["rating"] == 4
    assert update_response.json()["comment"] == "Still very helpful."


@pytest.mark.integration
def test_user_cannot_create_duplicate_specialist_review(
    client: TestClient,
    user_factory: Callable[..., User],
    specialist_factory: Callable[..., Specialist],
    auth_headers_factory,
) -> None:
    """Reject duplicate reviews from the same user for the same specialist."""

    # Arrange
    user = user_factory()
    specialist = specialist_factory(full_name="Dr. Duplicate")
    headers = auth_headers_factory(user)
    first_response = client.post(
        f"/api/v1/specialists/{specialist.id}/reviews",
        json={"rating": 5, "comment": "First review."},
        headers=headers,
    )
    assert first_response.status_code == 201

    # Act
    duplicate_response = client.post(
        f"/api/v1/specialists/{specialist.id}/reviews",
        json={"rating": 4, "comment": "Second review."},
        headers=headers,
    )

    # Assert
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "You have already reviewed this specialist."
