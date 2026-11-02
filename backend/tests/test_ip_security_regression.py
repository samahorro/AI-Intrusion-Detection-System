
"""KAN-231: Automated backend IP management security regression tests.

Tests IP input protection, database rollback, and simulated firewall safety.

No real operating-system firewall rules are modified.
Protected HTTP endpoint tests will follow KAN-230.
"""

import os
import subprocess

import pytest

from backend.app.ip_management.firewall import SimulatedFirewall
from backend.app.ip_management.permanent import (
    block_permanently,
    restore_permanent_blocks,
)
from backend.app.ip_management.service import IPBlockingService
from backend.app.ip_management.unblocking import unblock_saved_ip
from backend.app.models.blocked_ip import BlockedIP


class TrackingFirewall(SimulatedFirewall):
    """Count simulated firewall operations for security testing."""

    def __init__(self):
        super().__init__()
        self.block_calls = 0
        self.unblock_calls = 0

    def block_ip(self, ip_address):
        self.block_calls += 1
        return super().block_ip(ip_address)

    def unblock_ip(self, ip_address):
        self.unblock_calls += 1
        return super().unblock_ip(ip_address)


@pytest.mark.parametrize(
    "invalid_ip",
    [
        "",
        "not-an-ip",
        "example.com",
        "192.0.2.15/32",
        "192.0.2.15;whoami",
        "256.1.1.1",
        "2001:db8::1/128",
    ],
)
def test_invalid_block_request_has_no_side_effects(
    db_session,
    invalid_ip,
):
    firewall = TrackingFirewall()
    service = IPBlockingService(db_session, firewall)

    with pytest.raises(ValueError):
        service.block_ip(invalid_ip)

    assert db_session.query(BlockedIP).count() == 0
    assert firewall.block_calls == 0
    assert firewall.unblock_calls == 0


@pytest.mark.parametrize(
    "invalid_reason",
    [
        123,
        ["invalid"],
        "x" * 256,
    ],
)
def test_invalid_block_reason_does_not_modify_database(
    db_session,
    invalid_reason,
):
    firewall = TrackingFirewall()
    service = IPBlockingService(db_session, firewall)

    with pytest.raises(ValueError):
        service.block_ip(
            "192.0.2.80",
            reason=invalid_reason,
        )

    assert db_session.query(BlockedIP).count() == 0
    assert firewall.block_calls == 0


@pytest.mark.parametrize(
    "invalid_ip",
    [
        "not-an-ip",
        "192.0.2.81/24",
        "192.0.2.81;whoami",
    ],
)
def test_invalid_unblock_request_has_no_side_effects(
    db_session,
    invalid_ip,
):
    firewall = TrackingFirewall()
    service = IPBlockingService(db_session, firewall)

    with pytest.raises(ValueError):
        unblock_saved_ip(service, invalid_ip)

    assert db_session.query(BlockedIP).count() == 0
    assert firewall.unblock_calls == 0


def test_simulated_operations_never_execute_shell_commands(
    db_session,
    monkeypatch,
):
    def reject_command(*args, **kwargs):
        raise AssertionError(
            "IP management must not execute OS firewall commands."
        )

    monkeypatch.setattr(os, "system", reject_command)
    monkeypatch.setattr(subprocess, "run", reject_command)

    firewall = SimulatedFirewall()
    service = IPBlockingService(db_session, firewall)

    blocked = block_permanently(
        service,
        "192.0.2.90",
        reason="Security regression test",
    )

    assert blocked.success
    assert firewall.is_blocked("192.0.2.90")

    unblocked = unblock_saved_ip(service, "192.0.2.90")

    assert unblocked.success
    assert not firewall.is_blocked("192.0.2.90")


def test_database_failure_rolls_back_new_block(
    db_session,
    monkeypatch,
):
    firewall = SimulatedFirewall()
    service = IPBlockingService(db_session, firewall)

    def fail_commit():
        raise RuntimeError("Simulated database commit failure")

    monkeypatch.setattr(db_session, "commit", fail_commit)

    with pytest.raises(
        RuntimeError,
        match="Simulated database commit failure",
    ):
        service.block_ip("192.0.2.91")

    assert not firewall.is_blocked("192.0.2.91")
    assert db_session.query(BlockedIP).count() == 0


def test_database_failure_restores_previous_block(
    db_session,
    monkeypatch,
):
    firewall = SimulatedFirewall()
    service = IPBlockingService(db_session, firewall)

    service.block_ip("192.0.2.92")

    assert firewall.is_blocked("192.0.2.92")

    def fail_commit():
        raise RuntimeError("Simulated database commit failure")

    monkeypatch.setattr(db_session, "commit", fail_commit)

    with pytest.raises(
        RuntimeError,
        match="Simulated database commit failure",
    ):
        service.unblock_ip("192.0.2.92")

    record = service.get_record("192.0.2.92")

    assert record is not None
    assert record.status == "blocked"
    assert firewall.is_blocked("192.0.2.92")


def test_firewall_refusal_does_not_save_new_block(
    db_session,
):
    class RefusingFirewall(SimulatedFirewall):
        def block_ip(self, ip_address):
            return None

    firewall = RefusingFirewall()
    service = IPBlockingService(db_session, firewall)

    with pytest.raises(
        RuntimeError,
        match="could not block",
    ):
        service.block_ip("192.0.2.93")

    assert db_session.query(BlockedIP).count() == 0
    assert not firewall.is_blocked("192.0.2.93")


def test_permanent_block_restore_and_unblock_work_together(
    db_session,
):
    original_firewall = SimulatedFirewall()
    original_service = IPBlockingService(
        db_session,
        original_firewall,
    )

    result = block_permanently(
        original_service,
        "192.0.2.94",
        reason="Security regression test",
    )

    assert result.success

    restarted_firewall = SimulatedFirewall()
    restarted_service = IPBlockingService(
        db_session,
        restarted_firewall,
    )

    restored = restore_permanent_blocks(restarted_service)

    assert "192.0.2.94" in restored
    assert restarted_firewall.is_blocked("192.0.2.94")

    removed = unblock_saved_ip(
        restarted_service,
        "192.0.2.94",
    )

    assert removed.success
    assert not restarted_firewall.is_blocked("192.0.2.94")

    saved_record = restarted_service.get_record("192.0.2.94")

    assert saved_record is not None
    assert saved_record.status == "unblocked"
    assert saved_record.id == result.record_id
