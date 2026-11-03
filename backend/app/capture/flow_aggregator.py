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


class FlowTracker:
    """
    Stateful TCP/UDP flow tracker for experimental IDS testing.

    Emits finalized flows after inactivity, maximum duration,
    TCP reset, completed TCP FIN exchange, or packet limit.

    No ML inference or security alerts happen here.
    """

    def __init__(
        self,
        idle_timeout=30.0,
        max_duration=120.0,
        max_packets_per_flow=10000,
    ):
        self.idle_timeout = float(idle_timeout)
        self.max_duration = float(max_duration)
        self.max_packets_per_flow = int(max_packets_per_flow)

        if self.idle_timeout <= 0 or self.max_duration <= 0:
            raise ValueError("Flow timeouts must be positive")
        if self.max_packets_per_flow <= 0:
            raise ValueError("Packet limit must be positive")

        self.active_flows = {}

    def _key(self, packet):
        endpoints = _flow_key(packet)
        return (packet["protocol"], endpoints)

    def _finalize(self, key, reason):
        state = self.active_flows.pop(key)
        result = _build_flow(state["packets"])
        result["protocol"] = key[0]
        result["completion_reason"] = reason
        result["experimental"] = True
        return result

    def expire_flows(self, current_time):
        """Finalize expired flows at a given epoch timestamp."""
        completed = []

        for key, state in list(self.active_flows.items()):
            inactive = current_time - state["last_seen"]
            age = current_time - state["first_seen"]

            if inactive >= self.idle_timeout:
                completed.append(
                    self._finalize(key, "idle_timeout")
                )
            elif age >= self.max_duration:
                completed.append(
                    self._finalize(key, "max_duration")
                )

        return completed

    def add_packet(self, packet):
        """Process one normalized packet and return completed flows."""
        timestamp = float(packet["timestamp"])

        completed = self.expire_flows(timestamp)
        key = self._key(packet)

        if key not in self.active_flows:
            self.active_flows[key] = {
                "packets": [],
                "first_seen": timestamp,
                "last_seen": timestamp,
                "fin_directions": set(),
            }

        state = self.active_flows[key]
        state["packets"].append(packet)
        state["last_seen"] = max(state["last_seen"], timestamp)

        protocol = packet["protocol"]

        if protocol == "TCP":
            if packet.get("tcp_rst", False):
                completed.append(
                    self._finalize(key, "tcp_reset")
                )
                return completed

            if packet.get("tcp_fin", False):
                source = _endpoint(packet, "source")
                destination = _endpoint(packet, "destination")
                state["fin_directions"].add(
                    (source, destination)
                )

                if len(state["fin_directions"]) >= 2:
                    completed.append(
                        self._finalize(key, "tcp_fin_both_directions")
                    )
                    return completed

        if len(state["packets"]) >= self.max_packets_per_flow:
            completed.append(
                self._finalize(key, "packet_limit")
            )

        return completed

    def flush(self):
        """Finalize all active flows, such as when capture stops."""
        return [
            self._finalize(key, "capture_stopped")
            for key in list(self.active_flows)
        ]

    def reset(self):
        self.active_flows.clear()

    def active_count(self):
        return len(self.active_flows)
