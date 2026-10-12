import subprocess

import pytest

from backend.app.capture import capture_service


class FakeProcess:
    def __init__(self):
        self.returncode = None
        self.terminated = False
        self.killed = False
        self.stdout = None
    def poll(self):
        return self.returncode

    def terminate(self):
        self.terminated = True
        self.returncode = 0

    def wait(self, timeout=None):
        return self.returncode

    def kill(self):
        self.killed = True
        self.returncode = -9


def test_capture_service_starts(
    monkeypatch,
):
    fake_process = FakeProcess()
    captured_command = {}

    monkeypatch.setattr(
        capture_service,
        "resolve_capture_interface",
        lambda selector: "\\Device\\NPF_{WIFI}",
    )

    monkeypatch.setattr(
        capture_service,
        "get_tshark_path",
        lambda: "tshark",
    )

    def fake_popen(command, **kwargs):
        captured_command["command"] = command
        return fake_process

    monkeypatch.setattr(
        subprocess,
        "Popen",
        fake_popen,
    )

    service = capture_service.CaptureService()

    result = service.start("Wi-Fi")

    assert result["status"] == "running"
    assert service.is_running() is True

    assert "-i" in captured_command["command"]

    interface_index = (
        captured_command["command"].index("-i") + 1
    )

    assert (
        captured_command["command"][interface_index]
        == "\\Device\\NPF_{WIFI}"
    )


def test_capture_service_rejects_second_start(
    monkeypatch,
):
    fake_process = FakeProcess()

    monkeypatch.setattr(
        capture_service,
        "resolve_capture_interface",
        lambda selector: "\\Device\\NPF_{WIFI}",
    )

    monkeypatch.setattr(
        capture_service,
        "get_tshark_path",
        lambda: "tshark",
    )

    monkeypatch.setattr(
        subprocess,
        "Popen",
        lambda *args, **kwargs: fake_process,
    )

    service = capture_service.CaptureService()

    service.start("Wi-Fi")

    with pytest.raises(
        RuntimeError,
        match="already running",
    ):
        service.start("Wi-Fi")


def test_capture_service_stops(
    monkeypatch,
):
    fake_process = FakeProcess()

    monkeypatch.setattr(
        capture_service,
        "resolve_capture_interface",
        lambda selector: "\\Device\\NPF_{WIFI}",
    )

    monkeypatch.setattr(
        capture_service,
        "get_tshark_path",
        lambda: "tshark",
    )

    monkeypatch.setattr(
        subprocess,
        "Popen",
        lambda *args, **kwargs: fake_process,
    )

    service = capture_service.CaptureService()

    service.start("Wi-Fi")

    result = service.stop()

    assert result["status"] == "stopped"
    assert fake_process.terminated is True
    assert service.is_running() is False


def test_capture_service_rejects_stop_when_inactive():
    service = capture_service.CaptureService()

    with pytest.raises(
        RuntimeError,
        match="not running",
    ):
        service.stop()


def test_capture_service_start_failure(
    monkeypatch,
):
    monkeypatch.setattr(
        capture_service,
        "resolve_capture_interface",
        lambda selector: "\\Device\\NPF_{WIFI}",
    )

    monkeypatch.setattr(
        capture_service,
        "get_tshark_path",
        lambda: "tshark",
    )

    def raise_start_error(*args, **kwargs):
        raise OSError("process failed")

    monkeypatch.setattr(
        subprocess,
        "Popen",
        raise_start_error,
    )

    service = capture_service.CaptureService()

    with pytest.raises(
        RuntimeError,
        match="Unable to start",
    ):
        service.start("Wi-Fi")

    assert service.is_running() is False