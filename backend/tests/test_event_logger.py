import pytest

from backend.app.capture.event_logger import log_network_event
from backend.app.models.network_event import NetworkEvent


def valid_event(
    event_id: str = "evt-0001",
) -> dict:
    return {
        "event_id": event_id,
        "session_id": 10001,
        "timestamp": "2026-10-06T20:30:00Z",
        "src_ip": "192.168.1.15",
        "dest_ip": "192.168.1.20",
        "protocol": "TCP",
        "src_port": 51000,
        "dest_port": 443,
        "payload_size": 1200,
        "direction": "outbound",
    }


def test_log_network_event_persists_event(
    db_session,
):
    event = valid_event()

    logged_event = log_network_event(
        db_session,
        event,
    )

    stored_event = (
        db_session.query(NetworkEvent)
        .filter_by(event_id="evt-0001")
        .one()
    )

    assert logged_event.event_id == "evt-0001"
    assert stored_event.session_id == 10001
    assert stored_event.timestamp == (
        "2026-10-06T20:30:00Z"
    )
    assert stored_event.src_ip == (
        "192.168.1.15"
    )
    assert stored_event.dest_ip == (
        "192.168.1.20"
    )
    assert stored_event.protocol == "TCP"
    assert stored_event.src_port == 51000
    assert stored_event.dest_port == 443
    assert stored_event.payload_size == 1200
    assert stored_event.direction == "outbound"


def test_log_network_event_supports_null_ports(
    db_session,
):
    event = valid_event("evt-icmp")

    event["protocol"] = "ICMP"
    event["src_port"] = None
    event["dest_port"] = None
    event["payload_size"] = 64

    logged_event = log_network_event(
        db_session,
        event,
    )

    assert logged_event.protocol == "ICMP"
    assert logged_event.src_port is None
    assert logged_event.dest_port is None
    assert logged_event.payload_size == 64


def test_invalid_event_is_not_logged(
    db_session,
):
    event = valid_event()
    event["src_ip"] = "not-an-ip"

    with pytest.raises(
        ValueError,
        match="src_ip",
    ):
        log_network_event(
            db_session,
            event,
        )

    count = (
        db_session.query(NetworkEvent)
        .count()
    )

    assert count == 0


def test_multiple_network_events_persist(
    db_session,
):
    first_event = valid_event(
        "evt-0001"
    )

    second_event = valid_event(
        "evt-0002"
    )

    second_event["dest_ip"] = "8.8.8.8"

    log_network_event(
        db_session,
        first_event,
    )

    log_network_event(
        db_session,
        second_event,
    )

    stored_events = (
        db_session.query(NetworkEvent)
        .all()
    )

    assert len(stored_events) == 2


def test_duplicate_event_id_rejected(
    db_session,
):
    event = valid_event(
        "evt-duplicate"
    )

    log_network_event(
        db_session,
        event,
    )

    with pytest.raises(
        RuntimeError,
        match="Failed to log network event",
    ):
        log_network_event(
            db_session,
            event,
        )

    stored_events = (
        db_session.query(NetworkEvent)
        .filter_by(
            event_id="evt-duplicate"
        )
        .all()
    )

    assert len(stored_events) == 1