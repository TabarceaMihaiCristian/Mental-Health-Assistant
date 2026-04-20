"""Integration tests for basic health endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_check_returns_ok_status(client: TestClient) -> None:
    """Return a successful health payload for a reachable API process."""

    # Arrange

    # Act
    response = client.get("/api/v1/health")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
