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


def test_get_tshark_path_uses_configured_path(
    monkeypatch,
    tmp_path,
):
    tshark = tmp_path / "tshark"
    tshark.write_text("fake executable")

    monkeypatch.setenv(
        "TSHARK_PATH",
        str(tshark),
    )

    result = interface_service.get_tshark_path()

    assert result == str(tshark)


def test_get_tshark_path_rejects_missing_configured_path(
    monkeypatch,
    tmp_path,
):
    missing = tmp_path / "missing-tshark"

    monkeypatch.setenv(
        "TSHARK_PATH",
        str(missing),
    )

    with pytest.raises(
        RuntimeError,
        match="TShark was not found",
    ):
        interface_service.get_tshark_path()


def test_get_tshark_path_uses_system_path(
    monkeypatch,
):
    monkeypatch.delenv(
        "TSHARK_PATH",
        raising=False,
    )

    monkeypatch.setattr(
        interface_service.shutil,
        "which",
        lambda name: "C:\\mock\\tshark.exe",
    )

    result = interface_service.get_tshark_path()

    assert result == "C:\\mock\\tshark.exe"


def test_get_tshark_path_uses_known_path(
    monkeypatch,
):
    monkeypatch.delenv(
        "TSHARK_PATH",
        raising=False,
    )

    monkeypatch.setattr(
        interface_service.shutil,
        "which",
        lambda name: None,
    )

    class FakePath:
        def __init__(self, path):
            self.path = path

        def is_file(self):
            return (
                self.path
                == interface_service.WINDOWS_TSHARK_PATH
            )

    monkeypatch.setattr(
        interface_service,
        "Path",
        FakePath,
    )

    result = interface_service.get_tshark_path()

    assert (
        result
        == interface_service.WINDOWS_TSHARK_PATH
    )


def test_get_tshark_path_raises_when_not_found(
    monkeypatch,
):
    monkeypatch.delenv(
        "TSHARK_PATH",
        raising=False,
    )

    monkeypatch.setattr(
        interface_service.shutil,
        "which",
        lambda name: None,
    )

    class FakePath:
        def __init__(self, path):
            self.path = path

        def is_file(self):
            return False

    monkeypatch.setattr(
        interface_service,
        "Path",
        FakePath,
    )

    with pytest.raises(
        RuntimeError,
        match="TShark could not be found",
    ):
        interface_service.get_tshark_path()


def test_list_capture_interfaces(
    monkeypatch,
):
    monkeypatch.setattr(
        interface_service,
        "get_tshark_path",
        lambda: "tshark",
    )

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: (
            mock_interface_result()
        ),
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


def test_list_capture_interfaces_supports_no_description(
    monkeypatch,
):
    monkeypatch.setattr(
        interface_service,
        "get_tshark_path",
        lambda: "tshark",
    )

    result = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout="1. eth0\n",
        stderr="",
    )

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: result,
    )

    interfaces = (
        interface_service.list_capture_interfaces()
    )

    assert interfaces == [
        {
            "number": 1,
            "name": "eth0",
            "description": None,
        }
    ]


def test_list_capture_interfaces_skips_unrecognized_lines(
    monkeypatch,
):
    monkeypatch.setattr(
        interface_service,
        "get_tshark_path",
        lambda: "tshark",
    )

    result = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout=(
            "not an interface\n"
            "2. \\Device\\NPF_{WIFI} (Wi-Fi)\n"
        ),
        stderr="",
    )

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: result,
    )

    interfaces = (
        interface_service.list_capture_interfaces()
    )

    assert len(interfaces) == 1
    assert interfaces[0]["number"] == 2


def test_list_capture_interfaces_timeout(
    monkeypatch,
):
    monkeypatch.setattr(
        interface_service,
        "get_tshark_path",
        lambda: "tshark",
    )

    def raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(
            cmd=["tshark", "-D"],
            timeout=10,
        )

    monkeypatch.setattr(
        subprocess,
        "run",
        raise_timeout,
    )

    with pytest.raises(
        RuntimeError,
        match="Timed out while listing",
    ):
        interface_service.list_capture_interfaces()


def test_list_capture_interfaces_process_failure(
    monkeypatch,
):
    monkeypatch.setattr(
        interface_service,
        "get_tshark_path",
        lambda: "tshark",
    )

    def raise_failure(*args, **kwargs):
        raise subprocess.CalledProcessError(
            returncode=1,
            cmd=["tshark", "-D"],
        )

    monkeypatch.setattr(
        subprocess,
        "run",
        raise_failure,
    )

    with pytest.raises(
        RuntimeError,
        match="Unable to list capture interfaces",
    ):
        interface_service.list_capture_interfaces()


def test_list_capture_interfaces_rejects_empty_output(
    monkeypatch,
):
    monkeypatch.setattr(
        interface_service,
        "get_tshark_path",
        lambda: "tshark",
    )

    result = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout="not a valid interface line\n",
        stderr="",
    )

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: result,
    )

    with pytest.raises(
        RuntimeError,
        match="No capture interfaces were found",
    ):
        interface_service.list_capture_interfaces()


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


def test_resolve_interface_by_number(
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
            "2"
        )
    )

    assert result == "\\Device\\NPF_{WIFI}"


def test_resolve_interface_by_name_case_insensitive(
    monkeypatch,
):
    monkeypatch.setattr(
        interface_service,
        "list_capture_interfaces",
        lambda: [
            {
                "number": 2,
                "name": "WiFi0",
                "description": None,
            }
        ],
    )

    result = (
        interface_service.resolve_capture_interface(
            "wifi0"
        )
    )

    assert result == "WiFi0"


def test_resolve_interface_trims_selector(
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
            "  Wi-Fi  "
        )
    )

    assert result == "\\Device\\NPF_{WIFI}"


def test_empty_interface_rejected():
    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        interface_service.resolve_capture_interface(
            ""
        )


def test_unknown_interface_rejected(
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

    with pytest.raises(
        ValueError,
        match="was not found",
    ):
        interface_service.resolve_capture_interface(
            "Fake Interface"
        )