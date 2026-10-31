
"""KAN-229: IP unblocking and safety regression tests."""

import pytest

from backend.app.ip_management.firewall import SimulatedFirewall
from backend.app.ip_management.service import IPBlockingService
from backend.app.ip_management.unblocking import unblock_saved_ip
from backend.app.models.blocked_ip import BlockedIP


def test_unblock_preserves_record_and_clears_simulation(db_session):
    firewall = SimulatedFirewall()
    service = IPBlockingService(db_session, firewall)

    original = service.block_ip(
        "192.0.2.70",
        reason="Test scan",
    )

    result = unblock_saved_ip(service, "192.0.2.70")

    assert result.success
    assert result.changed
    assert result.simulated
    assert result.status == "unblocked"
    assert result.record_id == original.record_id

    saved = db_session.get(BlockedIP, original.record_id)
    assert saved.status == "unblocked"
    assert not firewall.is_blocked("192.0.2.70")


def test_repeated_unblock_is_idempotent(db_session):
    service = IPBlockingService(
        db_session,
        SimulatedFirewall(),
    )

    service.block_ip("192.0.2.71")

    first = unblock_saved_ip(service, "192.0.2.71")
    second = unblock_saved_ip(service, "192.0.2.71")

    assert first.changed is True
    assert second.success
    assert second.changed is False
    assert first.record_id == second.record_id

    assert db_session.query(BlockedIP).count() == 1


def test_unknown_ip_returns_not_found_without_creating_row(db_session):
    service = IPBlockingService(
        db_session,
        SimulatedFirewall(),
    )

    result = unblock_saved_ip(service, "192.0.2.72")

    assert not result.success
    assert not result.changed
    assert result.status == "not_found"
    assert result.record_id is None

    assert db_session.query(BlockedIP).count() == 0


def test_unblock_saved_record_after_simulator_restart(db_session):
    original = IPBlockingService(
        db_session,
        SimulatedFirewall(),
    )

    original.block_ip("192.0.2.73")

    restarted = IPBlockingService(
        db_session,
        SimulatedFirewall(),
    )

    result = unblock_saved_ip(restarted, "192.0.2.73")

    assert result.success
    assert result.changed

    assert (
        restarted.get_record("192.0.2.73").status
        == "unblocked"
    )

    assert not restarted.firewall.is_blocked("192.0.2.73")


def test_unblock_clears_stale_simulated_entry(db_session):
    firewall = SimulatedFirewall()
    service = IPBlockingService(db_session, firewall)

    service.block_ip("192.0.2.74")

    record = service.get_record("192.0.2.74")
    record.status = "unblocked"
    db_session.commit()

    assert firewall.is_blocked("192.0.2.74")

    result = unblock_saved_ip(service, "192.0.2.74")

    assert result.success
    assert result.changed
    assert not firewall.is_blocked("192.0.2.74")

    assert (
        service.get_record("192.0.2.74").status
        == "unblocked"
    )


def test_unblocked_ip_can_be_blocked_again(db_session):
    service = IPBlockingService(
        db_session,
        SimulatedFirewall(),
    )

    original = service.block_ip("192.0.2.75")

    unblock_saved_ip(service, "192.0.2.75")

    again = service.block_ip("192.0.2.75")

    assert again.record_id == original.record_id
    assert again.status == "blocked"
    assert service.firewall.is_blocked("192.0.2.75")


def test_ipv6_is_normalized(db_session):
    service = IPBlockingService(
        db_session,
        SimulatedFirewall(),
    )

    service.block_ip("2001:db8::76")

    result = unblock_saved_ip(
        service,
        "2001:0db8::76",
    )

    assert result.success
    assert result.ip_address == "2001:db8::76"

    assert not service.firewall.is_blocked("2001:db8::76")


@pytest.mark.parametrize(
    "invalid",
    [
        "not-an-ip",
        "192.0.2.0/24",
        "192.0.2.77;echo",
    ],
)
def test_invalid_address_is_rejected(db_session, invalid):
    service = IPBlockingService(
        db_session,
        SimulatedFirewall(),
    )

    with pytest.raises(ValueError):
        unblock_saved_ip(service, invalid)

    assert db_session.query(BlockedIP).count() == 0


def test_simulator_refusal_rolls_back_database_change(db_session):

    class RefusingUnblockFirewall(SimulatedFirewall):
        def unblock_ip(self, ip_address):
            return None

    firewall = RefusingUnblockFirewall()
    service = IPBlockingService(db_session, firewall)

    service.block_ip("192.0.2.78")

    with pytest.raises(RuntimeError, match="could not unblock"):
        unblock_saved_ip(service, "192.0.2.78")

    assert (
        service.get_record("192.0.2.78").status
        == "blocked"
    )

    assert firewall.is_blocked("192.0.2.78")


def test_requires_ip_blocking_service():
    with pytest.raises(
        TypeError,
        match="IPBlockingService",
    ):
        unblock_saved_ip(
            object(),
            "192.0.2.79",
        )
