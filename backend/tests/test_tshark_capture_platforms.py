import importlib
import os
import sys

from backend.app.capture import tshark_capture


def test_default_tshark_path_for_macos(
    monkeypatch,
):
    original_os_name = os.name
    original_platform = sys.platform

    try:
        monkeypatch.setattr(
            os,
            "name",
            "posix",
        )

        monkeypatch.setattr(
            sys,
            "platform",
            "darwin",
        )

        reloaded = importlib.reload(
            tshark_capture
        )

        assert reloaded.DEFAULT_TSHARK_PATH == (
            "/Applications/Wireshark.app/"
            "Contents/MacOS/tshark"
        )

    finally:
        monkeypatch.setattr(
            os,
            "name",
            original_os_name,
        )

        monkeypatch.setattr(
            sys,
            "platform",
            original_platform,
        )

        importlib.reload(
            tshark_capture
        )


def test_default_tshark_path_for_linux(
    monkeypatch,
):
    original_os_name = os.name
    original_platform = sys.platform

    try:
        monkeypatch.setattr(
            os,
            "name",
            "posix",
        )

        monkeypatch.setattr(
            sys,
            "platform",
            "linux",
        )

        reloaded = importlib.reload(
            tshark_capture
        )

        assert (
            reloaded.DEFAULT_TSHARK_PATH
            == "tshark"
        )

    finally:
        monkeypatch.setattr(
            os,
            "name",
            original_os_name,
        )

        monkeypatch.setattr(
            sys,
            "platform",
            original_platform,
        )

        importlib.reload(
            tshark_capture
        )