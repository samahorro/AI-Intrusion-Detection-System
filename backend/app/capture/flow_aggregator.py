from typing import Any


def _endpoint(
    packet: dict[str, Any],
    direction: str,
) -> tuple[str, int | None]:
    return (
        packet[f"{direction}_ip"],
        packet[f"{direction}_port"],
    )


def _flow_key(
    packet: dict[str, Any],
) -> tuple[
    tuple[str, int | None],
    tuple[str, int | None],
]:
    """
    Create a bidirectional flow key.

    A -> B and B -> A packets belong to the same flow.
    """

    source = _endpoint(
        packet,
        "source",
    )

    destination = _endpoint(
        packet,
        "destination",
    )

    return tuple(
        sorted(
            (source, destination),
            key=lambda endpoint: (
                endpoint[0],
                endpoint[1]
                if endpoint[1] is not None
                else -1,
            ),
        )
    )


def _build_flow(
    packets: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Convert packets from one connection into IDS flow features.
    """

    packets = sorted(
        packets,
        key=lambda packet: packet["timestamp"],
    )

    first_packet = packets[0]

    first_source = _endpoint(
        first_packet,
        "source",
    )

    first_destination = _endpoint(
        first_packet,
        "destination",
    )

    start_time = float(
        first_packet["timestamp"]
    )

    end_time = float(
        packets[-1]["timestamp"]
    )

    duration_seconds = max(
        end_time - start_time,
        0.0,
    )

    duration_microseconds = (
        duration_seconds * 1_000_000
    )

    forward_packets = 0
    backward_packets = 0
    total_bytes = 0

    for packet in packets:
        source = _endpoint(
            packet,
            "source",
        )

        destination = _endpoint(
            packet,
            "destination",
        )

        total_bytes += int(
            packet["length"]
        )

        if (
            source == first_source
            and destination
            == first_destination
        ):
            forward_packets += 1
        else:
            backward_packets += 1

    packet_count = len(packets)

    if duration_seconds > 0:
        bytes_per_second = (
            total_bytes / duration_seconds
        )

        packets_per_second = (
            packet_count / duration_seconds
        )
    else:
        bytes_per_second = 0.0
        packets_per_second = 0.0

    return {
        "source_ip": first_packet[
            "source_ip"
        ],
        "destination_ip": first_packet[
            "destination_ip"
        ],
        "source_port": first_packet[
            "source_port"
        ],
        "destination_port": first_packet[
            "destination_port"
        ],
        "packet_count": packet_count,
        "total_bytes": total_bytes,
        "flow": {
            "Flow Duration":
                duration_microseconds,
            "Total Fwd Packets":
                forward_packets,
            "Total Backward Packets":
                backward_packets,
            "Flow Bytes/s":
                bytes_per_second,
            "Flow Packets/s":
                packets_per_second,
        },
    }


def aggregate_packets(
    packets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Group captured packets into bidirectional network flows.
    """

    if not packets:
        return []

    grouped_packets: dict[
        tuple[
            tuple[str, int | None],
            tuple[str, int | None],
        ],
        list[dict[str, Any]],
    ] = {}

    for packet in sorted(
        packets,
        key=lambda item: item["timestamp"],
    ):
        key = _flow_key(packet)

        grouped_packets.setdefault(
            key,
            [],
        ).append(packet)

    return [
        _build_flow(flow_packets)
        for flow_packets
        in grouped_packets.values()
    ]