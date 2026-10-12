import pytest

from backend.app.capture.raw_event import (
    build_raw_event,
)


def test_build_outbound_raw_event():
    packet = {
        "timestamp": 0.0,
        "source_ip": "192.168.1.15",
        "destination_ip": "192.168.1.20",
        "protocol": "TCP",
        "source_port": 51000,
        "destination_port": 443,
        "length": 1200,
        "payload_size": 1200,
    }

    event = build_raw_event(
        packet=packet,
        session_id=10001,
        local_ip="192.168.1.15",
        event_id="evt-0001",
    )

    assert event == {
        "event_id": "evt-0001",
        "session_id": 10001,
        "timestamp": "1970-01-01T00:00:00Z",
        "src_ip": "192.168.1.15",
        "dest_ip": "192.168.1.20",
        "protocol": "TCP",
        "src_port": 51000,
        "dest_port": 443,
        "payload_size": 1200,
        "direction": "outbound",
    }


def test_build_inbound_raw_event():
    packet = {
        "timestamp": 0.0,
        "source_ip": "8.8.8.8",
        "destination_ip": "192.168.1.15",
        "protocol": "UDP",
        "source_port": 53,
        "destination_port": 53000,
        "length": 200,
        "payload_size": 200,
    }

    event = build_raw_event(
        packet=packet,
        session_id=10001,
        local_ip="192.168.1.15",
        event_id="evt-0002",
    )

    assert event["direction"] == "inbound"
    assert event["protocol"] == "UDP"
    assert event["src_ip"] == "8.8.8.8"
    assert event["dest_ip"] == "192.168.1.15"


def test_build_raw_event_generates_event_id():
    packet = {
        "timestamp": 0.0,
        "source_ip": "192.168.1.15",
        "destination_ip": "8.8.8.8",
        "protocol": "TCP",
        "source_port": 50000,
        "destination_port": 443,
        "length": 100,
        "payload_size": 100,
    }

    event = build_raw_event(
        packet=packet,
        session_id=10001,
        local_ip="192.168.1.15",
    )

    assert event["event_id"].startswith(
        "evt-"
    )


def test_build_raw_event_supports_no_ports():
    packet = {
        "timestamp": 0.0,
        "source_ip": "192.168.1.15",
        "destination_ip": "8.8.8.8",
        "protocol": "ICMP",
        "source_port": None,
        "destination_port": None,
        "length": 64,
        "payload_size": 64,
    }

    event = build_raw_event(
        packet=packet,
        session_id=10001,
        local_ip="192.168.1.15",
        event_id="evt-0003",
    )

    assert event["protocol"] == "ICMP"
    assert event["src_port"] is None
    assert event["dest_port"] is None


def test_unrelated_packet_direction_rejected():
    packet = {
        "timestamp": 0.0,
        "source_ip": "10.0.0.1",
        "destination_ip": "8.8.8.8",
        "protocol": "TCP",
        "source_port": 50000,
        "destination_port": 443,
        "length": 100,
        "payload_size": 100,
    }

    with pytest.raises(
        ValueError,
        match="does not involve",
    ):
        build_raw_event(
            packet=packet,
            session_id=10001,
            local_ip="192.168.1.15",
        )