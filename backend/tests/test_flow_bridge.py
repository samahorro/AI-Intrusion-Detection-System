from datetime import UTC, datetime

import pytest

from backend.app.capture.flow_bridge import FlowBridge


def packet(
    at,
    source,
    destination,
    sp,
    dp,
    length,
    protocol="TCP",
):
    return {
        "timestamp": datetime.fromtimestamp(
            at,
            UTC,
        ).isoformat(),
        "source_ip": source,
        "destination_ip": destination,
        "source_port": str(sp),
        "destination_port": str(dp),
        "length": length,
        "protocol": protocol,
    }


def test_bidirectional_flow_features_and_vector():
    bridge = FlowBridge()

    assert bridge.add_packet(
        packet(
            100,
            "10.0.0.1",
            "8.8.8.8",
            51000,
            443,
            100,
        )
    )

    assert bridge.add_packet(
        packet(
            100.5,
            "8.8.8.8",
            "10.0.0.1",
            443,
            51000,
            200,
        )
    )

    assert bridge.add_packet(
        packet(
            101,
            "10.0.0.1",
            "8.8.8.8",
            51000,
            443,
            300,
        )
    )

    result = bridge.snapshot()

    assert result["flow_count"] == 1

    flow = result["flows"][0]

    assert flow["feature_vector"] == pytest.approx(
        [
            1_000_000,
            2,
            1,
            600,
            3,
        ]
    )


def test_protocols_do_not_merge_and_reset():
    bridge = FlowBridge()

    bridge.add_packet(
        packet(
            100,
            "a",
            "b",
            55,
            80,
            100,
            "TCP",
        )
    )

    bridge.add_packet(
        packet(
            101,
            "a",
            "b",
            55,
            80,
            100,
            "UDP",
        )
    )

    assert bridge.snapshot()["flow_count"] == 2

    bridge.reset()

    assert bridge.snapshot()["flow_count"] == 0


def test_malformed_and_unsupported_packets_skipped():
    bridge = FlowBridge()

    assert not bridge.add_packet(
        packet(
            100,
            "a",
            "b",
            55,
            80,
            100,
            "OTHER",
        )
    )

    assert not bridge.add_packet(
        packet(
            100,
            "a",
            "b",
            "",
            80,
            100,
        )
    )

    assert bridge.snapshot()["window_packets"] == 0


def test_bounded_window():
    bridge = FlowBridge(
        max_packets=2,
    )

    for timestamp in range(3):
        bridge.add_packet(
            packet(
                100 + timestamp,
                "a",
                "b",
                55,
                80,
                100,
            )
        )

    assert bridge.snapshot()["window_packets"] == 2


def test_port_boundaries_are_accepted():
    bridge = FlowBridge()

    assert bridge.add_packet(
        packet(
            100,
            "10.0.0.1",
            "10.0.0.2",
            0,
            65535,
            100,
        )
    )

    assert bridge.snapshot()["window_packets"] == 1


def test_ports_outside_valid_range_are_rejected():
    bridge = FlowBridge()

    assert not bridge.add_packet(
        packet(
            100,
            "10.0.0.1",
            "10.0.0.2",
            -1,
            443,
            100,
        )
    )

    assert not bridge.add_packet(
        packet(
            101,
            "10.0.0.1",
            "10.0.0.2",
            50000,
            65536,
            100,
        )
    )

    assert bridge.snapshot()["window_packets"] == 0


def test_negative_packet_length_is_rejected():
    bridge = FlowBridge()

    assert not bridge.add_packet(
        packet(
            100,
            "10.0.0.1",
            "10.0.0.2",
            50000,
            443,
            -1,
        )
    )

    assert bridge.snapshot()["window_packets"] == 0


def test_out_of_order_packets_are_sorted_for_flow_metrics():
    bridge = FlowBridge()

    assert bridge.add_packet(
        packet(
            101,
            "10.0.0.1",
            "8.8.8.8",
            50000,
            443,
            200,
        )
    )

    assert bridge.add_packet(
        packet(
            100,
            "10.0.0.1",
            "8.8.8.8",
            50000,
            443,
            100,
        )
    )

    result = bridge.snapshot()

    assert result["flow_count"] == 1

    flow = result["flows"][0]

    assert flow["packet_count"] == 2
    assert flow["total_bytes"] == 300

    assert flow["features"]["Flow Duration"] == pytest.approx(
        1_000_000.0
    )

    assert flow["features"]["Flow Bytes/s"] == pytest.approx(
        300.0
    )

    assert flow["features"]["Flow Packets/s"] == pytest.approx(
        2.0
    )