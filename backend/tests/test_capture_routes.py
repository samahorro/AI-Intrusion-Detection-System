from unittest.mock import MagicMock

from backend.app.capture import routes as capture_routes


def test_capture_status_stopped(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        capture_routes.capture_service,
        "is_running",
        lambda: False,
    )

    response = client.get(
        "/capture/status"
    )

    assert response.status_code == 200

    assert response.json() == {
        "running": False,
        "interface": None,
    }


def test_capture_status_running(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        capture_routes.capture_service,
        "is_running",
        lambda: True,
    )

    monkeypatch.setattr(
        capture_routes.capture_service,
        "interface",
        "Wi-Fi",
    )

    response = client.get(
        "/capture/status"
    )

    assert response.status_code == 200

    assert response.json() == {
        "running": True,
        "interface": "Wi-Fi",
    }


def test_start_capture_success(
    client,
    monkeypatch,
):
    start_mock = MagicMock(
        return_value={
            "status": "running",
            "interface": "Wi-Fi",
        }
    )

    monkeypatch.setattr(
        capture_routes.capture_service,
        "start",
        start_mock,
    )

    response = client.post(
        "/capture/start",
        json={
            "interface": "Wi-Fi",
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "running",
        "interface": "Wi-Fi",
    }

    start_mock.assert_called_once_with(
        "Wi-Fi"
    )


def test_start_capture_rejects_duplicate(
    client,
    monkeypatch,
):
    def raise_duplicate(interface):
        raise RuntimeError(
            "Packet capture is already running."
        )

    monkeypatch.setattr(
        capture_routes.capture_service,
        "start",
        raise_duplicate,
    )

    response = client.post(
        "/capture/start",
        json={
            "interface": "Wi-Fi",
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Packet capture is already running."
    )


def test_start_capture_invalid_interface(
    client,
    monkeypatch,
):
    def raise_invalid_interface(interface):
        raise ValueError(
            "Unknown capture interface"
        )

    monkeypatch.setattr(
        capture_routes.capture_service,
        "start",
        raise_invalid_interface,
    )

    response = client.post(
        "/capture/start",
        json={
            "interface": "invalid",
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Unknown capture interface"
    )


def test_start_capture_service_failure(
    client,
    monkeypatch,
):
    def raise_failure(interface):
        raise RuntimeError(
            "Capture service failed"
        )

    monkeypatch.setattr(
        capture_routes.capture_service,
        "start",
        raise_failure,
    )

    response = client.post(
        "/capture/start",
        json={
            "interface": "Wi-Fi",
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Capture service failed"
    )


def test_stop_capture_success(
    client,
    monkeypatch,
):
    stop_mock = MagicMock(
        return_value={
            "status": "stopped",
            "interface": "Wi-Fi",
        }
    )

    monkeypatch.setattr(
        capture_routes.capture_service,
        "stop",
        stop_mock,
    )

    response = client.post(
        "/capture/stop"
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "stopped",
        "interface": "Wi-Fi",
    }

    stop_mock.assert_called_once()


def test_stop_capture_rejects_inactive(
    client,
    monkeypatch,
):
    def raise_inactive():
        raise RuntimeError(
            "Packet capture is not running."
        )

    monkeypatch.setattr(
        capture_routes.capture_service,
        "stop",
        raise_inactive,
    )

    response = client.post(
        "/capture/stop"
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Packet capture is not running."
    )


def test_stop_capture_service_failure(
    client,
    monkeypatch,
):
    def raise_failure():
        raise RuntimeError(
            "Capture stop failed"
        )

    monkeypatch.setattr(
        capture_routes.capture_service,
        "stop",
        raise_failure,
    )

    response = client.post(
        "/capture/stop"
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Capture stop failed"
    )