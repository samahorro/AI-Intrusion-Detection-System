import subprocess

import pytest

from backend.app.capture.tshark_capture import (
    capture_packets,
)


def test_capture_packets_parses_tcp_packets(
    monkeypatch,
):
    output = (
        "100.5|192.168.1.10|8.8.8.8|6|100|50000|443||\n"
        "101.0|8.8.8.8|192.168.1.10|6|200|443|50000||\n"
    )

    completed_process = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout=output,
        stderr="",
    )

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: completed_process,
    )

    packets = capture_packets(
        interface="en0",
        packet_count=2,
    )

    assert len(packets) == 2

    assert packets[0] == {
        "timestamp": 100.5,
        "source_ip": "192.168.1.10",
        "destination_ip": "8.8.8.8",
        "protocol": "TCP",
        "source_port": 50000,
        "destination_port": 443,
        "length": 100,
        "payload_size": 100,
    }


def test_capture_packets_supports_udp(
    monkeypatch,
):
    output = (
        "100.0|10.0.0.1|8.8.8.8|17|80|||5353|53\n"
    )

    completed_process = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout=output,
        stderr="",
    )

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: completed_process,
    )

    packets = capture_packets(
        interface="en0",
        packet_count=1,
    )

    assert packets[0]["protocol"] == "UDP"
    assert packets[0]["source_port"] == 5353
    assert packets[0]["destination_port"] == 53
    assert packets[0]["payload_size"] == 80


def test_capture_packets_supports_icmp(
    monkeypatch,
):
    output = (
        "100.0|10.0.0.1|8.8.8.8|1|64||||\n"
    )

    completed_process = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout=output,
        stderr="",
    )

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: completed_process,
    )

    packets = capture_packets(
        interface="en0",
        packet_count=1,
    )

    assert packets[0]["protocol"] == "ICMP"
    assert packets[0]["source_port"] is None
    assert packets[0]["destination_port"] is None
    assert packets[0]["payload_size"] == 64


def test_capture_packets_skips_invalid_rows(
    monkeypatch,
):
    output = (
        "invalid-row\n"
        "100.0||||100|50000|443||\n"
        "bad-time|10.0.0.1|8.8.8.8|6|100|50000|443||\n"
        "101.0|10.0.0.1|8.8.8.8|6|120|50000|443||\n"
    )

    completed_process = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout=output,
        stderr="",
    )

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: completed_process,
    )

    packets = capture_packets(
        interface="en0",
        packet_count=4,
    )

    assert len(packets) == 1
    assert packets[0]["length"] == 120
    assert packets[0]["payload_size"] == 120
    assert packets[0]["protocol"] == "TCP"


def test_invalid_packet_count_rejected():
    with pytest.raises(
        ValueError,
        match="packet_count",
    ):
        capture_packets(
            interface="en0",
            packet_count=0,
        )


def test_empty_interface_rejected():
    with pytest.raises(
        ValueError,
        match="interface",
    ):
        capture_packets(
            interface="",
            packet_count=5,
        )


def test_missing_tshark_raises_runtime_error(
    monkeypatch,
):
    def raise_missing(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(
        subprocess,
        "run",
        raise_missing,
    )

    with pytest.raises(
        RuntimeError,
        match="TShark was not found",
    ):
        capture_packets(
            interface="en0",
            packet_count=5,
        )


def test_tshark_timeout_raises_runtime_error(
    monkeypatch,
):
    def raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(
            cmd="tshark",
            timeout=30,
        )

    monkeypatch.setattr(
        subprocess,
        "run",
        raise_timeout,
    )

    with pytest.raises(
        RuntimeError,
        match="timed out",
    ):
        capture_packets(
            interface="en0",
            packet_count=5,
        )


def test_tshark_failure_raises_runtime_error(
    monkeypatch,
):
    def raise_failure(*args, **kwargs):
        raise subprocess.CalledProcessError(
            returncode=1,
            cmd="tshark",
            stderr="capture permission denied",
        )

    monkeypatch.setattr(
        subprocess,
        "run",
        raise_failure,
    )

    with pytest.raises(
        RuntimeError,
        match="capture permission denied",
    ):
        capture_packets(
            interface="en0",
            packet_count=5,
        )