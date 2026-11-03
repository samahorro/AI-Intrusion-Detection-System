
"""Tests for Sprint 4 IP address validation."""

import pytest

from backend.app.ip_management.validation import validate_ip_address


@pytest.mark.parametrize(
    "value, expected",
    [
        ("192.168.1.1", "192.168.1.1"),
        ("8.8.8.8", "8.8.8.8"),
        ("2001:0db8::1", "2001:db8::1"),
        ("::1", "::1"),
    ],
)
def test_valid_ip_address(value, expected):
    assert validate_ip_address(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        None,
        123,
        "300.1.1.1",
        "192.168.1.0/24",
        "invalid-ip",
        "google.com",
        "127.0.0.1; rm -rf /",
        " 192.168.1.1",
        "192.168.1.1 ",
        "2001:db8::bad::1",
    ],
)
def test_invalid_ip_address(value):
    with pytest.raises(ValueError):
        validate_ip_address(value)
