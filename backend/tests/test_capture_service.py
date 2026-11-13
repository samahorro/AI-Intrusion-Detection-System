import io
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


def test_capture_service_starts(monkeypatch):
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

    interface_index = captured_command["command"].index("-i") + 1

    assert (
        captured_command["command"][interface_index]
        == "\\Device\\NPF_{WIFI}"
    )


def test_capture_service_rejects_second_start(monkeypatch):
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


def test_capture_service_stops(monkeypatch):
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


def test_capture_service_start_failure(monkeypatch):
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


def test_capture_service_reads_tcp_packet():
    service = capture_service.CaptureService()

    process = FakeProcess()

    process.stdout = io.StringIO(
        "1700000000.5|192.0.2.10||198.51.100.20||"
        "128|50000|443|||1|0|0\n"
    )

    service._read_packets(
        process,
        service._generation,
    )

    stats = service.get_stats()

    assert stats["packet_count"] == 1
    assert stats["total_bytes"] == 128
    assert stats["protocols"] == {"TCP": 1}
    assert stats["observed_source_ips"] == 1

    packet = stats["recent_packets"][0]

    assert packet["source_ip"] == "192.0.2.10"
    assert packet["destination_ip"] == "198.51.100.20"
    assert packet["source_port"] == "50000"
    assert packet["destination_port"] == "443"
    assert packet["protocol"] == "TCP"
    assert packet["length"] == 128

    assert packet["tcp_syn"] is True
    assert packet["tcp_fin"] is False
    assert packet["tcp_rst"] is False


def test_capture_service_reads_udp_ipv6_packet():
    service = capture_service.CaptureService()

    process = FakeProcess()

    process.stdout = io.StringIO(
        "1700000001.5||2001:db8::10||2001:db8::20|"
        "256|||5353|53|0|0|0\n"
    )

    service._read_packets(
        process,
        service._generation,
    )

    stats = service.get_stats()

    assert stats["packet_count"] == 1
    assert stats["total_bytes"] == 256
    assert stats["protocols"] == {"UDP": 1}
    assert stats["observed_source_ips"] == 1

    packet = stats["recent_packets"][0]

    assert packet["source_ip"] == "2001:db8::10"
    assert packet["destination_ip"] == "2001:db8::20"
    assert packet["source_port"] == "5353"
    assert packet["destination_port"] == "53"
    assert packet["protocol"] == "UDP"
    assert packet["length"] == 256

    assert packet["tcp_syn"] is False
    assert packet["tcp_fin"] is False
    assert packet["tcp_rst"] is False


def test_capture_service_skips_malformed_packet():
    service = capture_service.CaptureService()

    process = FakeProcess()

    process.stdout = io.StringIO(
        "this|packet|does|not|have|enough|fields\n"
    )

    service._read_packets(
        process,
        service._generation,
    )

    stats = service.get_stats()

    assert stats["packet_count"] == 0
    assert stats["total_bytes"] == 0
    assert stats["protocols"] == {}
    assert stats["recent_packets"] == []


def test_capture_service_reads_other_protocol_packet():
    service = capture_service.CaptureService()

    process = FakeProcess()

    process.stdout = io.StringIO(
        "1700000002.5|192.0.2.30||198.51.100.40||"
        "64|||||0|0|0\n"
    )

    service._read_packets(
        process,
        service._generation,
    )

    stats = service.get_stats()

    assert stats["packet_count"] == 1
    assert stats["total_bytes"] == 64
    assert stats["protocols"] == {"OTHER": 1}

    packet = stats["recent_packets"][0]

    assert packet["source_ip"] == "192.0.2.30"
    assert packet["destination_ip"] == "198.51.100.40"
    assert packet["protocol"] == "OTHER"
    assert packet["source_port"] is None
    assert packet["destination_port"] is None


def test_capture_service_skips_invalid_numeric_packet_data():
    service = capture_service.CaptureService()

    process = FakeProcess()

    process.stdout = io.StringIO(
        "bad-time|192.0.2.10||198.51.100.20||"
        "128|50000|443|||1|0|0\n"
        "1700000000.5|192.0.2.10||198.51.100.20||"
        "not-a-size|50000|443|||1|0|0\n"
    )

    service._read_packets(
        process,
        service._generation,
    )

    stats = service.get_stats()

    assert stats["packet_count"] == 0
    assert stats["total_bytes"] == 0
    assert stats["protocols"] == {}
    assert stats["recent_packets"] == []


def test_capture_service_starts_packet_reader_thread(monkeypatch):
    fake_process = FakeProcess()
    fake_process.stdout = io.StringIO("")

    thread_started = {"value": False}

    class FakeThread:
        def __init__(
            self,
            target=None,
            args=None,
            daemon=None,
            name=None,
        ):
            self.target = target
            self.args = args
            self.daemon = daemon
            self.name = name

        def start(self):
            thread_started["value"] = True

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

    monkeypatch.setattr(
        capture_service.threading,
        "Thread",
        FakeThread,
    )

    service = capture_service.CaptureService()

    result = service.start("Wi-Fi")

    assert result["status"] == "running"
    assert thread_started["value"] is True


def test_capture_service_stops_stale_packet_reader():
    service = capture_service.CaptureService()

    process = FakeProcess()

    process.stdout = io.StringIO(
        "1700000003.5|192.0.2.10||198.51.100.20||"
        "128|50000|443|||1|0|0\n"
    )

    stale_generation = service._generation + 1

    service._read_packets(
        process,
        stale_generation,
    )

    stats = service.get_stats()

    assert stats["packet_count"] == 0
    assert stats["total_bytes"] == 0
    assert stats["recent_packets"] == []


def test_capture_service_records_packet_reader_error():
    service = capture_service.CaptureService()

    class BrokenOutput:
        def __iter__(self):
            return self

        def __next__(self):
            raise OSError("packet reader failed")

        def close(self):
            pass

    process = FakeProcess()
    process.stdout = BrokenOutput()

    service._read_packets(
        process,
        service._generation,
    )

    stats = service.get_stats()

    assert stats["last_error"] == "packet reader failed"


def test_capture_service_kills_process_after_stop_timeout():
    service = capture_service.CaptureService()

    class TimeoutProcess(FakeProcess):
        def __init__(self):
            super().__init__()
            self.wait_calls = 0

        def wait(self, timeout=None):
            self.wait_calls += 1

            if self.wait_calls == 1:
                raise subprocess.TimeoutExpired(
                    cmd="tshark",
                    timeout=timeout,
                )

            return self.returncode

    class FlushableBridge:
        def __init__(self):
            self.flushed = False

        def flush(self):
            self.flushed = True

    process = TimeoutProcess()
    bridge = FlushableBridge()

    service.process = process
    service.interface = "\\Device\\NPF_{WIFI}"
    service.flow_bridge = bridge

    result = service.stop()

    assert result["status"] == "stopped"
    assert result["interface"] == "\\Device\\NPF_{WIFI}"

    assert process.terminated is True
    assert process.killed is True
    assert process.wait_calls == 2

    assert bridge.flushed is True

    assert service.process is None
    assert service.interface is None