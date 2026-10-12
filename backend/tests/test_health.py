from fastapi.testclient import TestClient

import backend.app.main as main_module


def test_health_endpoint_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
    }


def test_backend_app_starts_without_database_initialization(
    monkeypatch,
):
    init_called = False

    def fake_init_db():
        nonlocal init_called
        init_called = True

    monkeypatch.setattr(
        main_module,
        "init_db",
        fake_init_db,
    )

    application = main_module.create_app(
        initialize_database=False,
    )

    assert init_called is False

    with TestClient(application) as test_client:
        response = test_client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_backend_app_initializes_database_by_default(
    monkeypatch,
):
    init_calls = 0

    def fake_init_db():
        nonlocal init_calls
        init_calls += 1

    monkeypatch.setattr(
        main_module,
        "init_db",
        fake_init_db,
    )

    application = main_module.create_app()

    assert init_calls == 1
    assert application.title == (
        "AI Intrusion Detection System API"
    )
    assert application.version == "0.3.0"


def test_backend_startup_registers_core_routes():
    application = main_module.create_app(
        initialize_database=False,
    )

    paths = application.openapi()["paths"]

    assert "/health" in paths
    assert "/auth/register" in paths
    assert "/detection/analyze" in paths
    assert "/capture/status" in paths