from datetime import UTC, datetime
from typing import Any, TypedDict
from uuid import uuid4


class RawEvent(TypedDict):
    """Backend network event contract."""

    event_id: str
    session_id: int
    timestamp: str
    src_ip: str
    dest_ip: str
    protocol: str
    src_port: int | None
    dest_port: int | None
    payload_size: int
    direction: str


def _format_timestamp(
    timestamp: float | str,
) -> str:
    """Convert an epoch timestamp to UTC ISO-8601."""

    parsed_timestamp = float(timestamp)

    return (
        datetime.fromtimestamp(
            parsed_timestamp,
            tz=UTC,
        )
        .isoformat()
        .replace("+00:00", "Z")
    )


def _determine_direction(
    source_ip: str,
    destination_ip: str,
    local_ip: str,
) -> str:
    """Determine packet direction relative to this host."""

    if source_ip == local_ip:
        return "outbound"

    if destination_ip == local_ip:
        return "inbound"

    raise ValueError(
        "Packet does not involve the selected local IP."
    )


def build_raw_event(
    packet: dict[str, Any],
    session_id: int,
    local_ip: str,
    event_id: str | None = None,
) -> RawEvent:
    """Convert packet metadata into the RawEvent contract."""

    source_ip = str(packet["source_ip"])
    destination_ip = str(
        packet["destination_ip"]
    )

    source_port = packet.get(
        "source_port"
    )

    destination_port = packet.get(
        "destination_port"
    )

    return {
        "event_id": (
            event_id
            or f"evt-{uuid4().hex[:12]}"
        ),
        "session_id": int(session_id),
        "timestamp": _format_timestamp(
            packet["timestamp"]
        ),
        "src_ip": source_ip,
        "dest_ip": destination_ip,
        "protocol": str(
            packet["protocol"]
        ).upper(),
        "src_port": (
            int(source_port)
            if source_port is not None
            else None
        ),
        "dest_port": (
            int(destination_port)
            if destination_port is not None
            else None
        ),
        "payload_size": int(
            packet["payload_size"]
        ),
        "direction": _determine_direction(
            source_ip,
            destination_ip,
            local_ip,
        ),
    }