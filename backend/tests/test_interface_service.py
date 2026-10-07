import subprocess

import pytest

from backend.app.capture import interface_service

INTERFACE_OUTPUT = (
    "1. \\Device\\NPF_{BLUETOOTH} "
    "(Bluetooth Network Connection)\n"
    "2. \\Device\\NPF_{WIFI} (Wi-Fi)\n"
    "3. \\Device\\NPF_{ETHERNET} (Ethernet)\n"
)


def mock_interface_result():
    return subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout=INTERFACE_OUTPUT,
        stderr="",
    )


def test_list_capture_interfaces(monkeypatch):
    monkeypatch.setattr(
        interface_service,
        "get_tshark_path",
        lambda: "tshark",
    )

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: mock_interface_result(),
    )

    interfaces = (
        interface_service.list_capture_interfaces()
    )

    assert len(interfaces) == 3
    assert interfaces[1]["number"] == 2
    assert interfaces[1]["description"] == "Wi-Fi"
    assert (
        interfaces[1]["name"]
        == "\\Device\\NPF_{WIFI}"
    )


def test_resolve_interface_by_description(
    monkeypatch,
):
    monkeypatch.setattr(
        interface_service,
        "list_capture_interfaces",
        lambda: [
            {
                "number": 2,
                "name": "\\Device\\NPF_{WIFI}",
                "description": "Wi-Fi",
            }
        ],
    )

    result = (
        interface_service.resolve_capture_interface(
            "Wi-Fi"
        )
    )

    assert result == "\\Device\\NPF_{WIFI}"


def test_resolve_interface_by_number(monkeypatch):
    monkeypatch.setattr(
        interface_service,
        "list_capture_interfaces",
        lambda: [
            {
                "number": 2,
                "name": "\\Device\\NPF_{WIFI}",
                "description": "Wi-Fi",
            }
        ],
    )

    result = (
        interface_service.resolve_capture_interface(
            "2"
        )
    )

    assert result == "\\Device\\NPF_{WIFI}"


def test_empty_interface_rejected():
    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        interface_service.resolve_capture_interface("")


def test_unknown_interface_rejected(monkeypatch):
    monkeypatch.setattr(
        interface_service,
        "list_capture_interfaces",
        lambda: [
            {
                "number": 2,
                "name": "\\Device\\NPF_{WIFI}",
                "description": "Wi-Fi",
            }
        ],
    )

    with pytest.raises(
        ValueError,
        match="was not found",
    ):
        interface_service.resolve_capture_interface(
            "Fake Interface"
        )