from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.models.network_event import (
    NetworkEvent,
)

from .raw_event_validator import validate_raw_event


def log_network_event(
    db: Session,
    event: dict[str, Any],
) -> NetworkEvent:
    """Validate and persist a network event."""

    validated_event = validate_raw_event(
        event
    )

    network_event = NetworkEvent(
        event_id=validated_event["event_id"],
        session_id=validated_event[
            "session_id"
        ],
        timestamp=validated_event[
            "timestamp"
        ],
        src_ip=validated_event["src_ip"],
        dest_ip=validated_event["dest_ip"],
        protocol=validated_event["protocol"],
        src_port=validated_event["src_port"],
        dest_port=validated_event[
            "dest_port"
        ],
        payload_size=validated_event[
            "payload_size"
        ],
        direction=validated_event[
            "direction"
        ],
    )

    try:
        db.add(network_event)
        db.commit()
        db.refresh(network_event)

    except SQLAlchemyError as exc:
        db.rollback()

        raise RuntimeError(
            "Failed to log network event"
        ) from exc

    return network_event