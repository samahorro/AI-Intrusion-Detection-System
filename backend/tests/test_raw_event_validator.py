import pytest

from backend.app.capture.raw_event_validator import (
    validate_raw_event,
)


def valid_event():
    return {
        "event_id": "evt-0001",
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


def test_valid_raw_event_passes():
    event = valid_event()

    validated = validate_raw_event(event)

    assert validated == event


def test_missing_required_field_rejected():
    event = valid_event()
    del event["src_ip"]

    with pytest.raises(
        ValueError,
        match="Missing required fields",
    ):
        validate_raw_event(event)


def test_empty_event_id_rejected():
    event = valid_event()
    event["event_id"] = ""

    with pytest.raises(
        ValueError,
        match="event_id",
    ):
        validate_raw_event(event)


def test_invalid_session_id_rejected():
    event = valid_event()
    event["session_id"] = 0

    with pytest.raises(
        ValueError,
        match="session_id",
    ):
        validate_raw_event(event)


def test_invalid_timestamp_rejected():
    event = valid_event()
    event["timestamp"] = "not-a-timestamp"

    with pytest.raises(
        ValueError,
        match="timestamp",
    ):
        validate_raw_event(event)


def test_invalid_source_ip_rejected():
    event = valid_event()
    event["src_ip"] = "999.999.999.999"

    with pytest.raises(
        ValueError,
        match="src_ip",
    ):
        validate_raw_event(event)


def test_invalid_destination_ip_rejected():
    event = valid_event()
    event["dest_ip"] = "not-an-ip"

    with pytest.raises(
        ValueError,
        match="dest_ip",
    ):
        validate_raw_event(event)


def test_empty_protocol_rejected():
    event = valid_event()
    event["protocol"] = ""

    with pytest.raises(
        ValueError,
        match="protocol",
    ):
        validate_raw_event(event)


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("src_port", -1),
        ("src_port", 65536),
        ("dest_port", -1),
        ("dest_port", 65536),
    ],
)
def test_invalid_ports_rejected(
    field_name,
    value,
):
    event = valid_event()
    event[field_name] = value

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        validate_raw_event(event)


def test_none_ports_allowed():
    event = valid_event()
    event["protocol"] = "ICMP"
    event["src_port"] = None
    event["dest_port"] = None

    validated = validate_raw_event(event)

    assert validated["src_port"] is None
    assert validated["dest_port"] is None


def test_negative_payload_size_rejected():
    event = valid_event()
    event["payload_size"] = -1

    with pytest.raises(
        ValueError,
        match="payload_size",
    ):
        validate_raw_event(event)


def test_invalid_direction_rejected():
    event = valid_event()
    event["direction"] = "sideways"

    with pytest.raises(
        ValueError,
        match="direction",
    ):
        validate_raw_event(event)