
"""Sprint 4 Task 3: blocked IP database persistence tests."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from backend.app.models.blocked_ip import BlockedIP


def test_block_record_persists_across_sessions(session_factory):
    first_session = session_factory()

    try:
        record = BlockedIP(
            ip_address="192.0.2.10",
            block_type="permanent",
            reason="Sprint 4 test",
        )

        first_session.add(record)
        first_session.commit()
        record_id = record.id

    finally:
        first_session.close()

    second_session = session_factory()

    try:
        saved = second_session.get(BlockedIP, record_id)

        assert saved is not None
        assert saved.ip_address == "192.0.2.10"
        assert saved.block_type == "permanent"
        assert saved.status == "blocked"
        assert saved.reason == "Sprint 4 test"
        assert saved.expires_at is None
        assert saved.created_at is not None
        assert saved.updated_at is not None

    finally:
        second_session.close()


def test_block_status_can_be_updated(db_session):
    block = BlockedIP(
        ip_address="198.51.100.20"
    )

    db_session.add(block)
    db_session.commit()

    block.status = "unblocked"
    db_session.commit()
    db_session.refresh(block)

    assert block.status == "unblocked"


def test_temporary_block_expiration_is_stored(db_session):
    expires = datetime.now(UTC) + timedelta(hours=1)

    block = BlockedIP(
        ip_address="203.0.113.50",
        block_type="temporary",
        expires_at=expires,
    )

    db_session.add(block)
    db_session.commit()
    db_session.refresh(block)

    assert block.block_type == "temporary"
    assert block.expires_at is not None

    saved_expiration = block.expires_at.replace(tzinfo=UTC)

    assert abs(
        (saved_expiration - expires).total_seconds()
    ) < 1


def test_ipv6_is_normalized_before_storing(db_session):
    block = BlockedIP(
        ip_address="2001:0db8::1"
    )

    db_session.add(block)
    db_session.commit()

    assert block.ip_address == "2001:db8::1"


def test_duplicate_ip_is_rejected(db_session):
    db_session.add(
        BlockedIP(ip_address="192.0.2.10")
    )
    db_session.commit()

    db_session.add(
        BlockedIP(ip_address="192.0.2.10")
    )

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()

    assert db_session.query(BlockedIP).count() == 1


def test_invalid_ip_is_rejected_before_database_write(db_session):
    with pytest.raises(ValueError):
        BlockedIP(ip_address="not-an-ip")

    assert db_session.query(BlockedIP).count() == 0


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        ("block_type", "forever"),
        ("status", "unknown"),
    ],
)
def test_invalid_block_fields_are_rejected(
    db_session,
    field,
    bad_value,
):
    kwargs = {field: bad_value}

    db_session.add(
        BlockedIP(
            ip_address="203.0.113.33",
            **kwargs,
        )
    )

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_rollback_does_not_save_block(db_session):
    db_session.add(
        BlockedIP(ip_address="203.0.113.40")
    )

    db_session.rollback()

    assert db_session.query(BlockedIP).count() == 0
