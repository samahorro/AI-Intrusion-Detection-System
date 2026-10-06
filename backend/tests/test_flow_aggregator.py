import pytest

from backend.app.capture.flow_aggregator import (
    aggregate_packets,
)


def test_bidirectional_packets_become_one_flow():
    packets = [
        {
            "timestamp": 100.0,
            "source_ip": "192.168.1.10",
            "destination_ip": "8.8.8.8",
            "source_port": 50000,
            "destination_port": 443,
            "length": 100,
        },
        {
            "timestamp": 100.5,
            "source_ip": "8.8.8.8",
            "destination_ip": "192.168.1.10",
            "source_port": 443,
            "destination_port": 50000,
            "length": 200,
        },
        {
            "timestamp": 101.0,
            "source_ip": "192.168.1.10",
            "destination_ip": "8.8.8.8",
            "source_port": 50000,
            "destination_port": 443,
            "length": 300,
        },
    ]

    flows = aggregate_packets(
        packets
    )

    assert len(flows) == 1

    result = flows[0]

    assert result["packet_count"] == 3
    assert result["total_bytes"] == 600

    flow = result["flow"]

    assert flow[
        "Flow Duration"
    ] == pytest.approx(
        1_000_000.0
    )

    assert flow[
        "Total Fwd Packets"
    ] == 2

    assert flow[
        "Total Backward Packets"
    ] == 1

    assert flow[
        "Flow Bytes/s"
    ] == pytest.approx(
        600.0
    )

    assert flow[
        "Flow Packets/s"
    ] == pytest.approx(
        3.0
    )


def test_separate_connections_create_separate_flows():
    packets = [
        {
            "timestamp": 100.0,
            "source_ip": "10.0.0.1",
            "destination_ip": "8.8.8.8",
            "source_port": 50000,
            "destination_port": 443,
            "length": 100,
        },
        {
            "timestamp": 101.0,
            "source_ip": "10.0.0.1",
            "destination_ip": "1.1.1.1",
            "source_port": 50001,
            "destination_port": 443,
            "length": 100,
        },
    ]

    flows = aggregate_packets(
        packets
    )

    assert len(flows) == 2


def test_zero_duration_flow_has_zero_rates():
    packets = [
        {
            "timestamp": 100.0,
            "source_ip": "10.0.0.1",
            "destination_ip": "8.8.8.8",
            "source_port": 50000,
            "destination_port": 443,
            "length": 100,
        }
    ]

    flows = aggregate_packets(
        packets
    )

    flow = flows[0]["flow"]

    assert flow["Flow Duration"] == 0.0
    assert flow["Flow Bytes/s"] == 0.0
    assert flow["Flow Packets/s"] == 0.0


def test_empty_packet_list_returns_empty_flows():
    assert aggregate_packets([]) == []