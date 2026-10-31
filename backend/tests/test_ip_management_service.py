"""KAN-227: backend blocking service with an in-memory firewall."""

import pytest

from backend.app.ip_management.firewall import SimulatedFirewall
from backend.app.ip_management.service import IPBlockingService


def test_block_ip_saves_record_and_updates_simulator(db_session):
    firewall = SimulatedFirewall()
    service = IPBlockingService(db_session, firewall)

    result = service.block_ip("192.0.2.40", reason="Test scan")

    assert result.success is True
    assert result.changed is True
    assert result.status == "blocked"
    assert result.simulated is True
    assert firewall.is_blocked("192.0.2.40")
    assert service.get_record("192.0.2.40").reason == "Test scan"


def test_unblock_ip_updates_record_and_simulator(db_session):
    firewall = SimulatedFirewall()
    service = IPBlockingService(db_session, firewall)
    service.block_ip("192.0.2.41")

    result = service.unblock_ip("192.0.2.41")

    assert result.success is True
    assert result.status == "unblocked"
    assert not firewall.is_blocked("192.0.2.41")
    assert service.get_record("192.0.2.41").status == "unblocked"


def test_blocking_same_ip_twice_does_not_duplicate_record(db_session):
    service = IPBlockingService(db_session, SimulatedFirewall())
    first = service.block_ip("192.0.2.42")
    second = service.block_ip("192.0.2.42")

    assert first.record_id == second.record_id
    assert second.changed is False


def test_reblocking_uses_same_saved_record(db_session):
    service = IPBlockingService(db_session, SimulatedFirewall())
    first = service.block_ip("192.0.2.43")
    service.unblock_ip("192.0.2.43")
    again = service.block_ip("192.0.2.43")

    assert first.record_id == again.record_id
    assert again.status == "blocked"


def test_unknown_ip_has_no_record(db_session):
    service = IPBlockingService(db_session, SimulatedFirewall())
    assert service.get_record("192.0.2.44") is None
    assert service.unblock_ip("192.0.2.44").status == "not_found"


def test_invalid_ip_is_rejected(db_session):
    service = IPBlockingService(db_session, SimulatedFirewall())
    with pytest.raises(ValueError):
        service.block_ip("192.0.2.0/24")


def test_reject_real_firewall_adapter(db_session):
    with pytest.raises(TypeError, match="SimulatedFirewall only"):
        IPBlockingService(db_session, object())