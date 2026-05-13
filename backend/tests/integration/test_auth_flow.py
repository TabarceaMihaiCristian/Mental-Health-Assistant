"""Integration tests for local authentication flows."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.fixtures.auth import TEST_AUTH_SECRET

PASSWORD_FIELD = "password"


def test_register_login_and_me_flow(client: TestClient) -> None:
    """Allow a user to register, log in, and fetch the current profile."""

    payload = {
        "email": "auth-flow@example.com",
        "full_name": "Auth Flow User",
        PASSWORD_FIELD: TEST_AUTH_SECRET,
    }

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

    assert register_response.status_code == 201
    assert register_response.json()["user"]["email"] == payload["email"]
    assert login_response.status_code == 200
    assert login_response.json()["token_type"] == "bearer"
    assert me_response.status_code == 200
    assert me_response.json()["email"] == payload["email"]
    assert me_response.json()["full_name"] == payload["full_name"]


def test_login_rejects_invalid_credentials(client: TestClient) -> None:
    """Reject login attempts that provide the wrong password."""

    client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrong-password@example.com",
            "full_name": "Wrong Password User",
            PASSWORD_FIELD: TEST_AUTH_SECRET,
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrong-password@example.com",
            PASSWORD_FIELD: "WrongPass" + "999!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


def test_forgot_and_reset_password_flow(client: TestClient) -> None:
    """Allow a user to request a reset token, reset the password, and log in with the new secret."""

    email = "reset-flow@example.com"
    rotated_secret = f"{TEST_AUTH_SECRET}-reset"
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Reset Flow User",
            PASSWORD_FIELD: TEST_AUTH_SECRET,
        },
    )

    forgot_response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": email},
    )
    reset_token = forgot_response.json()["reset_token"]
    reset_response = client.post(
        "/api/v1/auth/reset-password",
        json={"token": reset_token, PASSWORD_FIELD: rotated_secret},
    )
    stale_reset_response = client.post(
        "/api/v1/auth/reset-password",
        json={"token": reset_token, PASSWORD_FIELD: TEST_AUTH_SECRET},
    )
    old_login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, PASSWORD_FIELD: TEST_AUTH_SECRET},
    )
    new_login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, PASSWORD_FIELD: rotated_secret},
    )

    assert forgot_response.status_code == 200
    assert forgot_response.json()["message"] == (
        "If an account with that email exists, password reset instructions have been generated."
    )
    assert reset_token
    assert reset_response.status_code == 200
    assert reset_response.json()["message"] == (
        "Your password has been updated. You can now sign in with the new password."
    )
    assert stale_reset_response.status_code == 400
    assert stale_reset_response.json()["detail"] == "Invalid or expired password reset token."
    assert old_login_response.status_code == 401
    assert new_login_response.status_code == 200


def test_forgot_password_keeps_unknown_emails_generic(client: TestClient) -> None:
    """Do not reveal whether an account exists when password reset is requested."""

    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "missing@example.com"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == (
        "If an account with that email exists, password reset instructions have been generated."
    )
    assert response.json()["reset_token"] is None
