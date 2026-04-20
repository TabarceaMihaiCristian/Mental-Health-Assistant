"""Integration tests for local authentication flows."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.fixtures.auth import TEST_AUTH_SECRET

PASSWORD_FIELD = "password"


def test_register_login_and_me_flow(client: TestClient) -> None:
    """Allow a user to register, log in, and fetch the current profile."""

    # Arrange
    payload = {
        "email": "auth-flow@example.com",
        "full_name": "Auth Flow User",
        PASSWORD_FIELD: TEST_AUTH_SECRET,
    }

    # Act
    register_response = client.post("/api/v1/auth/register", json=payload)
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], PASSWORD_FIELD: TEST_AUTH_SECRET},
    )
    token = login_response.json()["access_token"]
    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Assert
    assert register_response.status_code == 201
    assert register_response.json()["user"]["email"] == payload["email"]
    assert login_response.status_code == 200
    assert login_response.json()["token_type"] == "bearer"
    assert me_response.status_code == 200
    assert me_response.json()["email"] == payload["email"]
    assert me_response.json()["full_name"] == payload["full_name"]


def test_login_rejects_invalid_credentials(client: TestClient) -> None:
    """Reject login attempts that provide the wrong password."""

    # Arrange
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrong-password@example.com",
            "full_name": "Wrong Password User",
            PASSWORD_FIELD: TEST_AUTH_SECRET,
        },
    )

    # Act
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrong-password@example.com",
            PASSWORD_FIELD: "WrongPass" + "999!",
        },
    )

    # Assert
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."
