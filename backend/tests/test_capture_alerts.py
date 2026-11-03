
"""KAN-253: Automated intrusion-detection regression tests."""

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from backend.app.main import create_app
from backend.app.capture.flow_bridge import FlowBridge


def make_packet(port, syn=True, ack=False):
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_ip": "192.0.2.10",
        "destination_ip": "192.0.2.20",
        "source_port": 50000,
        "destination_port": port,
        "protocol": "TCP",
        "length": 60,
        "tcp_syn": syn,
        "tcp_ack": ack,
        "tcp_fin": False,
        "tcp_rst": False,
    }


def test_no_alert_below_threshold():
    bridge = FlowBridge()

    for port in range(20, 39):
        assert bridge.add_packet(make_packet(port))

    assert bridge.get_alerts() == []


def test_alert_generated_at_threshold():
    bridge = FlowBridge()

    for port in range(20, 40):
        assert bridge.add_packet(make_packet(port))

    alerts = bridge.get_alerts()

    assert len(alerts) == 1
    assert alerts[0]["detected"] is True
    assert alerts[0]["rule_id"] == "AEGIS-SIG-002"
    assert alerts[0]["attack_type"] == "port_scan"
    assert alerts[0]["ports_scanned"] == 20


def test_duplicate_alert_suppression():
    bridge = FlowBridge()

    for port in range(20, 50):
        assert bridge.add_packet(make_packet(port))

    assert len(bridge.get_alerts()) == 1


def test_syn_ack_packets_ignored():
    bridge = FlowBridge()

    for port in range(20, 50):
        assert bridge.add_packet(
            make_packet(port, syn=True, ack=True)
        )

    assert bridge.get_alerts() == []


def test_missing_ack_flag_not_counted():
    bridge = FlowBridge()

    for port in range(20, 50):
        packet = make_packet(port)
        del packet["tcp_ack"]

        assert bridge.add_packet(packet)

    assert bridge.get_alerts() == []


def test_reset_clears_alerts():
    bridge = FlowBridge()

    for port in range(20, 40):
        assert bridge.add_packet(make_packet(port))

    assert len(bridge.get_alerts()) == 1

    bridge.reset()

    assert bridge.get_alerts() == []


def test_unauthenticated_alert_access_denied():
    app = create_app(initialize_database=False)

    with TestClient(app) as client:
        response = client.get("/capture/alerts")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required."

def test_authenticated_user_can_retrieve_alerts():
    from unittest.mock import patch
    from backend.app.capture.capture_service import capture_service
    from backend.app.auth.dependencies import require_authenticated_user

    app = create_app(initialize_database=False)

    app.dependency_overrides[require_authenticated_user] = (
        lambda: {"id": 1, "username": "security_test_user"}
    )

    try:
        with patch.object(capture_service, "flow_bridge", FlowBridge()):
            for port in range(20, 40):
                capture_service.flow_bridge.add_packet(
                    make_packet(port)
                )

            with TestClient(app) as client:
                response = client.get("/capture/alerts")

            assert response.status_code == 200

            data = response.json()

            assert data["alert_count"] == 1
            assert len(data["alerts"]) == 1
            assert data["alerts"][0]["rule_id"] == "AEGIS-SIG-002"
            assert data["alerts"][0]["attack_type"] == "port_scan"

    finally:
        app.dependency_overrides.clear()
