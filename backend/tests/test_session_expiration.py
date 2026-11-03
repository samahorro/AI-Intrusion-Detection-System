"""Sprint 4 - Authentication session expiration tests."""

import secrets

from fastapi.testclient import TestClient

from backend.app.main import app


def register_and_login(client):
    """Create and authenticate a unique test account."""

    username = "s4timeout_" + secrets.token_hex(8)
    password = "S4!" + secrets.token_urlsafe(20)

    registration = client.post(
        "/auth/register",
        json={
            "username": username,
            "password": password,
        },
    )

    assert registration.status_code == 201

    login = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )

    assert login.status_code == 200

    return username, login


def test_session_cookie_expires_after_one_hour():
    """Session cookie must have a 3600-second lifetime."""

    with TestClient(app) as client:
        username, login = register_and_login(client)

        cookie = login.headers.get(
            "set-cookie",
            "",
        ).lower()

        assert username
        assert "max-age=3600" in cookie
        assert "httponly" in cookie
        assert "samesite=lax" in cookie


def test_authenticated_user_can_access_account():
    """Session expiration must not break authentication."""

    with TestClient(app) as client:
        username, login = register_and_login(client)

        assert login.status_code == 200

        response = client.get("/auth/me")

        assert response.status_code == 200
        assert response.json()["user"]["username"] == username


def test_unauthenticated_user_is_rejected():
    """Requests without a session remain unauthorized."""

    with TestClient(app) as client:
        response = client.get("/auth/me")

        assert response.status_code == 401
