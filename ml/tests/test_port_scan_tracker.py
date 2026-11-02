
"""SOC2-02: Port-scan detection security validation tests."""

from datetime import datetime, timezone

import pytest

from ml.detection.port_scan_tracker import PortScanTracker


def packet(port, timestamp=1000.0, **overrides):
    """Build a controlled synthetic TCP SYN packet."""
    event = {
        "protocol": "TCP",
        "tcp_syn": True,
        "tcp_ack": False,
        "source_ip": "192.0.2.10",
        "destination_ip": "192.0.2.20",
        "destination_port": port,
        "timestamp": timestamp,
    }
    event.update(overrides)
    return event


def test_19_ports_does_not_trigger():
    tracker = PortScanTracker()

    for port in range(20, 39):
        result = tracker.add_packet(packet(port))
        assert result is None


def test_20_ports_triggers_detection():
    tracker = PortScanTracker()

    for port in range(20, 39):
        assert tracker.add_packet(packet(port)) is None

    result = tracker.add_packet(packet(39))

    assert result is not None
    assert result["detected"] is True
    assert result["attack_type"] == "port_scan"
    assert result["rule_id"] == "AEGIS-SIG-002"
    assert result["severity"] == "medium"
    assert result["ports_scanned"] == 20


def test_duplicate_syn_packets_not_double_counted():
    tracker = PortScanTracker()

    for index in range(30):
        assert tracker.add_packet(packet(80, 1000 + index)) is None


def test_old_ports_expire_after_60_seconds():
    tracker = PortScanTracker(window_seconds=60)

    for port in range(20, 39):
        assert tracker.add_packet(packet(port, 1000)) is None

    # The previous 19 ports have expired.
    assert tracker.add_packet(packet(39, 1061)) is None


def test_syn_ack_not_counted():
    tracker = PortScanTracker()

    for port in range(20, 50):
        assert tracker.add_packet(
            packet(port, tcp_ack=True)
        ) is None


def test_udp_packets_not_counted():
    tracker = PortScanTracker()

    for port in range(20, 50):
        assert tracker.add_packet(
            packet(port, protocol="UDP")
        ) is None


@pytest.mark.parametrize(
    "invalid_port",
    [-1, 0, 65536, True, "80", None],
)
def test_invalid_destination_port_rejected(invalid_port):
    tracker = PortScanTracker()

    with pytest.raises(ValueError):
        tracker.add_packet(packet(invalid_port))


def test_invalid_timestamp_rejected():
    tracker = PortScanTracker()

    with pytest.raises(ValueError):
        tracker.add_packet(packet(80, timestamp="invalid"))


def test_reset_clears_tracking_state():
    tracker = PortScanTracker()

    for port in range(20, 39):
        tracker.add_packet(packet(port))

    tracker.reset()

    assert tracker.add_packet(packet(39)) is None
