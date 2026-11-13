from backend.app.capture import flow_bridge
from backend.app.capture.flow_bridge import FlowBridge


def valid_packet():
    return {
        "timestamp": "2026-10-06T20:30:00+00:00",
        "source_ip": "192.168.1.10",
        "destination_ip": "192.168.1.20",
        "source_port": 50000,
        "destination_port": 443,
        "protocol": "TCP",
        "length": 1200,
    }


def test_add_packet_rejects_missing_source_ip():
    bridge = FlowBridge()

    packet = valid_packet()
    packet["source_ip"] = ""

    assert bridge.add_packet(packet) is False

    assert (
        bridge.snapshot()["window_packets"]
        == 0
    )


def test_add_packet_returns_false_on_parse_error(
    monkeypatch,
):
    class FakeDateTime:
        @staticmethod
        def fromisoformat(value):
            raise OverflowError(
                "timestamp out of range"
            )

    monkeypatch.setattr(
        flow_bridge,
        "datetime",
        FakeDateTime,
    )

    bridge = FlowBridge()

    assert (
        bridge.add_packet(
            valid_packet()
        )
        is False
    )

    assert (
        bridge.snapshot()["window_packets"]
        == 0
    )


def test_snapshot_skips_invalid_flow_features(
    monkeypatch,
):
    bridge = FlowBridge()

    assert (
        bridge.add_packet(
            valid_packet()
        )
        is True
    )

    monkeypatch.setattr(
        flow_bridge,
        "REQUIRED_FEATURES",
        ("required_feature",),
    )

    monkeypatch.setattr(
        flow_bridge,
        "aggregate_packets",
        lambda packets: [
            {
                "source_ip": "192.168.1.10",
                "destination_ip": "192.168.1.20",
                "source_port": 50000,
                "destination_port": 443,
                "packet_count": 1,
                "total_bytes": 1200,
                "flow": {},
            }
        ],
    )

    result = bridge.snapshot()

    assert result["status"] == "preview_only"
    assert result["window_packets"] == 1
    assert result["flow_count"] == 0
    assert result["flows"] == []