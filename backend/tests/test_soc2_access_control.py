"""Sprint 4 SOC 2 CC6.1: reproducible logical-access-control evidence."""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import create_app
from backend.app.models.login_attempt import LoginAttempt


@pytest.mark.parametrize("path", [
    "/auth/me",
    "/capture/stats",
    "/capture/interfaces",
    "/capture/flows",
])
def test_anonymous_users_cannot_access_protected_resources(client, path):
    assert client.get(path).status_code == 401


def test_authenticated_user_can_view_own_identity(authenticated_client):
    response = authenticated_client.get("/auth/me")
    assert response.status_code == 200
    assert response.json()["user"]["username"] == "testuser"


def test_logout_revokes_access(authenticated_client):
    assert authenticated_client.post("/auth/logout").status_code == 200
    assert authenticated_client.get("/auth/me").status_code == 401


def test_failed_authentication_is_auditable(client, registered_user, db_session):
    response = client.post("/auth/login", json={
        "username": registered_user["username"],
        "password": "IncorrectPassword123!",
    })
    assert response.status_code == 401
    record = db_session.query(LoginAttempt).filter_by(
        username=registered_user["username"], success=False
    ).first()
    assert record is not None
    assert record.reason == "invalid_password"
    assert not hasattr(record, "password")


def test_production_rejects_insecure_secret(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("FRONTEND_ORIGIN", "https://aegis.example")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app(initialize_database=False)


def test_production_rejects_plaintext_frontend_origin(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "a" * 40)
    monkeypatch.setenv("FRONTEND_ORIGIN", "http://aegis.example")
    with pytest.raises(RuntimeError, match="HTTPS"):
        create_app(initialize_database=False)


def test_production_secure_headers_and_restricted_origins(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "b" * 40)
    monkeypatch.setenv("FRONTEND_ORIGIN", "https://aegis.example")
    app = create_app(initialize_database=False)
    with TestClient(app) as client:
        response = client.get("/health", headers={"Origin": "http://localhost:5173"})
        assert response.headers.get("access-control-allow-origin") is None
        assert response.headers["strict-transport-security"] == "max-age=31536000"
        assert response.headers["x-frame-options"] == "DENY"
        assert response.headers["cache-control"] == "no-store"
        response = client.get("/health", headers={"Origin": "https://aegis.example"})
        assert response.headers["access-control-allow-origin"] == "https://aegis.example"
