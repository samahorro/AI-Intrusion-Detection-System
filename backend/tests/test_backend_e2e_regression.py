from backend.app.capture.event_logger import (
    log_network_event,
)
from backend.app.capture.raw_event import (
    build_raw_event,
)
from backend.app.capture.raw_event_validator import (
    validate_raw_event,
)
from backend.app.models.network_event import (
    NetworkEvent,
)


def test_packet_to_persisted_network_event_e2e(
    db_session,
):
    packet = {
        "timestamp": 100.5,
        "source_ip": "192.168.1.15",
        "destination_ip": "8.8.8.8",
        "protocol": "TCP",
        "source_port": 51000,
        "destination_port": 443,
        "length": 1200,
        "payload_size": 1200,
    }

    raw_event = build_raw_event(
        packet=packet,
        session_id=10001,
        local_ip="192.168.1.15",
        event_id="evt-e2e-001",
    )

    validated_event = validate_raw_event(
        raw_event
    )

    logged_event = log_network_event(
        db_session,
        validated_event,
    )

    stored_event = (
        db_session.query(NetworkEvent)
        .filter_by(
            event_id="evt-e2e-001"
        )
        .one()
    )

    assert logged_event.event_id == (
        "evt-e2e-001"
    )

    assert stored_event.session_id == 10001

    assert stored_event.timestamp == (
        "1970-01-01T00:01:40.500000Z"
    )

    assert stored_event.src_ip == (
        "192.168.1.15"
    )

    assert stored_event.dest_ip == "8.8.8.8"

    assert stored_event.protocol == "TCP"

    assert stored_event.src_port == 51000

    assert stored_event.dest_port == 443

    assert stored_event.payload_size == 1200

    assert stored_event.direction == "outbound"


def test_inbound_packet_persists_correct_direction_e2e(
    db_session,
):
    packet = {
        "timestamp": 200.0,
        "source_ip": "8.8.8.8",
        "destination_ip": "192.168.1.15",
        "protocol": "UDP",
        "source_port": 53,
        "destination_port": 53000,
        "length": 256,
        "payload_size": 256,
    }

    raw_event = build_raw_event(
        packet=packet,
        session_id=10002,
        local_ip="192.168.1.15",
        event_id="evt-e2e-002",
    )

    validated_event = validate_raw_event(
        raw_event
    )

    log_network_event(
        db_session,
        validated_event,
    )

    stored_event = (
        db_session.query(NetworkEvent)
        .filter_by(
            event_id="evt-e2e-002"
        )
        .one()
    )

    assert stored_event.protocol == "UDP"

    assert stored_event.src_ip == "8.8.8.8"

    assert stored_event.dest_ip == (
        "192.168.1.15"
    )

    assert stored_event.src_port == 53

    assert stored_event.dest_port == 53000

    assert stored_event.payload_size == 256

    assert stored_event.direction == "inbound"


def test_unrelated_packet_does_not_reach_database_e2e(
    db_session,
):
    packet = {
        "timestamp": 300.0,
        "source_ip": "10.0.0.10",
        "destination_ip": "8.8.8.8",
        "protocol": "TCP",
        "source_port": 50000,
        "destination_port": 443,
        "length": 100,
        "payload_size": 100,
    }

    try:
        build_raw_event(
            packet=packet,
            session_id=10003,
            local_ip="192.168.1.15",
            event_id="evt-e2e-invalid",
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected unrelated packet to be rejected"
        )

    stored_events = (
        db_session.query(NetworkEvent)
        .filter_by(
            event_id="evt-e2e-invalid"
        )
        .all()
    )

    assert stored_events == []