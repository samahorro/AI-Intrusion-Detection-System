
"""Tests for Sprint 4 simulated firewall functionality."""

import os
import subprocess

import pytest

from backend.app.ip_management.firewall import SimulatedFirewall


def test_simulated_firewall_starts_empty():
    firewall = SimulatedFirewall()

    assert firewall.list_blocked_ips() == []
    assert firewall.is_blocked("192.0.2.10") is False


def test_block_valid_ipv4():
    firewall = SimulatedFirewall()

    result = firewall.block_ip("192.0.2.10")

    assert result.success is True
    assert result.action == "block"
    assert firewall.is_blocked("192.0.2.10") is True


def test_block_normalizes_ipv6():
    firewall = SimulatedFirewall()

    result = firewall.block_ip("2001:0db8::1")

    assert result.success is True
    assert result.ip_address == "2001:db8::1"
    assert firewall.is_blocked("2001:db8::1") is True


def test_duplicate_block_returns_failure():
    firewall = SimulatedFirewall()

    firewall.block_ip("192.0.2.10")
    result = firewall.block_ip("192.0.2.10")

    assert result.success is False
    assert result.message == "IP address is already blocked."


def test_unblock_existing_ip():
    firewall = SimulatedFirewall()

    firewall.block_ip("192.0.2.10")
    result = firewall.unblock_ip("192.0.2.10")

    assert result.success is True
    assert result.action == "unblock"
    assert firewall.is_blocked("192.0.2.10") is False


def test_unblock_missing_ip_returns_failure():
    firewall = SimulatedFirewall()

    result = firewall.unblock_ip("192.0.2.10")

    assert result.success is False
    assert result.message == "IP address is not currently blocked."


def test_can_block_again_after_unblock():
    firewall = SimulatedFirewall()

    firewall.block_ip("192.0.2.10")
    firewall.unblock_ip("192.0.2.10")

    result = firewall.block_ip("192.0.2.10")

    assert result.success is True
    assert firewall.is_blocked("192.0.2.10") is True


def test_multiple_ips_are_tracked():
    firewall = SimulatedFirewall()

    firewall.block_ip("192.0.2.10")
    firewall.block_ip("198.51.100.20")

    assert firewall.list_blocked_ips() == [
        "192.0.2.10",
        "198.51.100.20",
    ]


def test_instances_do_not_share_state():
    firewall_a = SimulatedFirewall()
    firewall_b = SimulatedFirewall()

    firewall_a.block_ip("192.0.2.10")

    assert firewall_a.is_blocked("192.0.2.10") is True
    assert firewall_b.is_blocked("192.0.2.10") is False


@pytest.mark.parametrize(
    "invalid_ip",
    [
        "300.1.1.1",
        "not-an-ip",
        "192.168.1.0/24",
        "127.0.0.1;echo unsafe",
        "",
        None,
    ],
)
def test_invalid_ip_cannot_be_blocked(invalid_ip):
    firewall = SimulatedFirewall()

    with pytest.raises(ValueError):
        firewall.block_ip(invalid_ip)

    assert firewall.list_blocked_ips() == []


def test_invalid_unblock_does_not_change_state():
    firewall = SimulatedFirewall()

    firewall.block_ip("192.0.2.10")

    with pytest.raises(ValueError):
        firewall.unblock_ip("invalid-ip")

    assert firewall.is_blocked("192.0.2.10") is True


def test_simulation_does_not_execute_system_commands(monkeypatch):
    def reject_system_command(*args, **kwargs):
        raise AssertionError(
            "Simulation must not execute operating-system commands."
        )

    monkeypatch.setattr(subprocess, "run", reject_system_command)
    monkeypatch.setattr(os, "system", reject_system_command)

    firewall = SimulatedFirewall()

    assert firewall.block_ip("192.0.2.10").success is True
    assert firewall.unblock_ip("192.0.2.10").success is True
