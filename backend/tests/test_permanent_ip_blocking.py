
"""KAN-228: verify durable permanent IP blocks and simulator restoration."""

import pytest

from backend.app.ip_management.firewall import SimulatedFirewall
from backend.app.ip_management.permanent import (
    block_permanently,
    restore_permanent_blocks,
)
from backend.app.ip_management.service import IPBlockingService
from backend.app.models.blocked_ip import BlockedIP


def test_permanent_block_is_saved_without_expiration(session_factory):
    with session_factory() as db:
        service = IPBlockingService(db, SimulatedFirewall())

        result = block_permanently(
            service,
            "192.0.2.50",
            reason="Suspicious traffic",
        )

        record_id = result.record_id

        assert result.success
        assert result.simulated

    with session_factory() as db:
        record = db.get(BlockedIP, record_id)

        assert record is not None
        assert record.ip_address == "192.0.2.50"
        assert record.status == "blocked"
        assert record.block_type == "permanent"
        assert record.expires_at is None
        assert record.reason == "Suspicious traffic"
        assert record.created_at is not None


def test_repeated_permanent_block_does_not_duplicate_record(db_session):
    service = IPBlockingService(db_session, SimulatedFirewall())

    first = block_permanently(service, "192.0.2.51")
    second = block_permanently(service, "192.0.2.51")

    assert first.changed is True
    assert second.changed is False
    assert first.record_id == second.record_id
    assert db_session.query(BlockedIP).count() == 1


def test_unblocked_ip_can_be_permanently_blocked_again(db_session):
    service = IPBlockingService(db_session, SimulatedFirewall())

    first = block_permanently(service, "192.0.2.52")

    service.unblock_ip("192.0.2.52")

    again = block_permanently(
        service,
        "192.0.2.52",
        reason="New event",
    )

    assert again.record_id == first.record_id
    assert again.changed is True
    assert service.get_record("192.0.2.52").reason == "New event"
    assert service.firewall.is_blocked("192.0.2.52")


def test_ipv6_address_is_normalized(db_session):
    service = IPBlockingService(db_session, SimulatedFirewall())

    result = block_permanently(service, "2001:0db8::2")

    assert result.ip_address == "2001:db8::2"
    assert service.get_record("2001:db8::2") is not None


@pytest.mark.parametrize(
    "bad_ip",
    [
        "example.com",
        "192.0.2.0/24",
        "8.8.8.8;echo",
    ],
)
def test_invalid_addresses_are_rejected(db_session, bad_ip):
    service = IPBlockingService(db_session, SimulatedFirewall())

    with pytest.raises(ValueError):
        block_permanently(service, bad_ip)

    assert db_session.query(BlockedIP).count() == 0


@pytest.mark.parametrize(
    "bad_reason",
    [
        "   ",
        "x" * 256,
        123,
    ],
)
def test_invalid_reasons_are_rejected(db_session, bad_reason):
    service = IPBlockingService(db_session, SimulatedFirewall())

    with pytest.raises(ValueError):
        block_permanently(
            service,
            "192.0.2.54",
            reason=bad_reason,
        )

    assert db_session.query(BlockedIP).count() == 0


def test_reason_whitespace_is_trimmed(db_session):
    service = IPBlockingService(db_session, SimulatedFirewall())

    block_permanently(
        service,
        "192.0.2.55",
        reason="  Traffic scan  ",
    )

    assert service.get_record("192.0.2.55").reason == "Traffic scan"


def test_permanent_blocks_can_be_restored_after_simulator_restart(db_session):
    original = IPBlockingService(db_session, SimulatedFirewall())

    block_permanently(original, "192.0.2.56")

    new_firewall = SimulatedFirewall()
    restored_service = IPBlockingService(db_session, new_firewall)

    assert not new_firewall.is_blocked("192.0.2.56")

    assert restore_permanent_blocks(restored_service) == (
        "192.0.2.56",
    )

    assert new_firewall.is_blocked("192.0.2.56")
    assert restore_permanent_blocks(restored_service) == ()


def test_restore_ignores_unblocked_records(db_session):
    first = IPBlockingService(db_session, SimulatedFirewall())

    block_permanently(first, "192.0.2.57")
    first.unblock_ip("192.0.2.57")

    new_firewall = SimulatedFirewall()

    restored = restore_permanent_blocks(
        IPBlockingService(db_session, new_firewall)
    )

    assert restored == ()
    assert not new_firewall.is_blocked("192.0.2.57")


def test_refused_simulation_rolls_back_database(db_session):
    class RefusingFirewall(SimulatedFirewall):
        def block_ip(self, ip_address):
            return None

    service = IPBlockingService(
        db_session,
        RefusingFirewall(),
    )

    with pytest.raises(RuntimeError, match="could not block"):
        block_permanently(service, "192.0.2.58")

    assert db_session.query(BlockedIP).count() == 0


def test_wrong_service_type_is_rejected():
    with pytest.raises(TypeError):
        block_permanently(object(), "192.0.2.59")

    with pytest.raises(TypeError):
        restore_permanent_blocks(object())
