from datetime import datetime
from ipaddress import ip_address
from typing import Any

from .raw_event import RawEvent

REQUIRED_FIELDS = {
    "event_id",
    "session_id",
    "timestamp",
    "src_ip",
    "dest_ip",
    "protocol",
    "src_port",
    "dest_port",
    "payload_size",
    "direction",
}


def _validate_timestamp(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            "timestamp must be a non-empty string"
        )

    normalized = value.replace(
        "Z",
        "+00:00",
    )

    try:
        parsed = datetime.fromisoformat(
            normalized
        )
    except ValueError as exc:
        raise ValueError(
            "timestamp must be valid ISO-8601"
        ) from exc

    if parsed.tzinfo is None:
        raise ValueError(
            "timestamp must include timezone information"
        )

    return value


def _validate_ip(
    value: Any,
    field_name: str,
) -> str:
    if not isinstance(value, str):
        raise TypeError(
            f"{field_name} must be a string"
        )

    try:
        ip_address(value)
    except ValueError as exc:
        raise ValueError(
            f"{field_name} must be a valid IP address"
        ) from exc

    return value


def _validate_port(
    value: Any,
    field_name: str,
) -> int | None:
    if value is None:
        return None

    if (
        isinstance(value, bool)
        or not isinstance(value, int)
    ):
        raise TypeError(
            f"{field_name} must be an integer or None"
        )

    if not 0 <= value <= 65535:
        raise ValueError(
            f"{field_name} must be between 0 and 65535"
        )

    return value


def validate_raw_event(
    event: dict[str, Any],
) -> RawEvent:
    """Validate a RawEvent before logging or storage."""

    missing_fields = REQUIRED_FIELDS - event.keys()

    if missing_fields:
        missing = ", ".join(
            sorted(missing_fields)
        )
        raise ValueError(
            f"Missing required fields: {missing}"
        )

    event_id = event["event_id"]

    if (
        not isinstance(event_id, str)
        or not event_id.strip()
    ):
        raise ValueError(
            "event_id must be a non-empty string"
        )

    session_id = event["session_id"]

    if (
        isinstance(session_id, bool)
        or not isinstance(session_id, int)
        or session_id <= 0
    ):
        raise ValueError(
            "session_id must be a positive integer"
        )

    timestamp = _validate_timestamp(
        event["timestamp"]
    )

    source_ip = _validate_ip(
        event["src_ip"],
        "src_ip",
    )

    destination_ip = _validate_ip(
        event["dest_ip"],
        "dest_ip",
    )

    protocol = event["protocol"]

    if (
        not isinstance(protocol, str)
        or not protocol.strip()
    ):
        raise ValueError(
            "protocol must be a non-empty string"
        )

    source_port = _validate_port(
        event["src_port"],
        "src_port",
    )

    destination_port = _validate_port(
        event["dest_port"],
        "dest_port",
    )

    payload_size = event["payload_size"]

    if (
        isinstance(payload_size, bool)
        or not isinstance(payload_size, int)
        or payload_size < 0
    ):
        raise ValueError(
            "payload_size must be a non-negative integer"
        )

    direction = event["direction"]

    if direction not in {
        "inbound",
        "outbound",
    }:
        raise ValueError(
            "direction must be inbound or outbound"
        )

    return {
        "event_id": event_id,
        "session_id": session_id,
        "timestamp": timestamp,
        "src_ip": source_ip,
        "dest_ip": destination_ip,
        "protocol": protocol.upper(),
        "src_port": source_port,
        "dest_port": destination_port,
        "payload_size": payload_size,
        "direction": direction,
    }