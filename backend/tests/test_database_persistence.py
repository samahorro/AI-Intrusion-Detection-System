import pytest

from backend.app.capture.event_logger import (
    log_network_event,
)
from backend.app.models.network_event import (
    NetworkEvent,
)


def valid_event(
    event_id: str,
) -> dict:
    return {
        "event_id": event_id,
        "session_id": 20001,
        "timestamp": "2026-10-11T20:00:00Z",
        "src_ip": "192.168.1.10",
        "dest_ip": "8.8.8.8",
        "protocol": "TCP",
        "src_port": 50000,
        "dest_port": 443,
        "payload_size": 512,
        "direction": "outbound",
    }


def test_network_event_persists_across_sessions(
    session_factory,
):
    first_session = session_factory()

    try:
        log_network_event(
            first_session,
            valid_event("evt-persist-001"),
        )
    finally:
        first_session.close()

    second_session = session_factory()

    try:
        stored_event = (
            second_session.query(NetworkEvent)
            .filter_by(
                event_id="evt-persist-001"
            )
            .one()
        )

        assert stored_event.session_id == 20001
        assert stored_event.src_ip == "192.168.1.10"
        assert stored_event.dest_ip == "8.8.8.8"
        assert stored_event.protocol == "TCP"
        assert stored_event.payload_size == 512

    finally:
        second_session.close()


def test_rollback_does_not_persist_uncommitted_event(
    session_factory,
):
    first_session = session_factory()

    event = NetworkEvent(
        event_id="evt-rollback-001",
        session_id=20002,
        timestamp="2026-10-11T20:01:00Z",
        src_ip="192.168.1.20",
        dest_ip="1.1.1.1",
        protocol="UDP",
        src_port=53000,
        dest_port=53,
        payload_size=128,
        direction="outbound",
    )

    try:
        first_session.add(event)
        first_session.rollback()
    finally:
        first_session.close()

    second_session = session_factory()

    try:
        stored_event = (
            second_session.query(NetworkEvent)
            .filter_by(
                event_id="evt-rollback-001"
            )
            .first()
        )

        assert stored_event is None

    finally:
        second_session.close()


def test_duplicate_failure_preserves_original_event(
    session_factory,
):
    first_session = session_factory()

    try:
        log_network_event(
            first_session,
            valid_event("evt-duplicate-isolation"),
        )

        with pytest.raises(
            RuntimeError,
            match="Failed to log network event",
        ):
            log_network_event(
                first_session,
                valid_event(
                    "evt-duplicate-isolation"
                ),
            )

    finally:
        first_session.close()

    verification_session = session_factory()

    try:
        stored_events = (
            verification_session.query(NetworkEvent)
            .filter_by(
                event_id="evt-duplicate-isolation"
            )
            .all()
        )

        assert len(stored_events) == 1

    finally:
        verification_session.close()


def test_isolated_test_database_starts_empty(
    db_session,
):
    count = (
        db_session.query(NetworkEvent)
        .count()
    )

    assert count == 0