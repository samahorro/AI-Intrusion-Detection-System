import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import TypedDict

WINDOWS_TSHARK_PATH = (
    r"C:\Program Files\Wireshark\tshark.exe"
)

MAC_TSHARK_PATH = (
    "/Applications/Wireshark.app/Contents/MacOS/tshark"
)


class CaptureInterface(TypedDict):
    number: int
    name: str
    description: str | None


def get_tshark_path() -> str:
    """Return an available TShark executable path."""

    configured_path = os.getenv("TSHARK_PATH")

    if configured_path:
        if Path(configured_path).is_file():
            return configured_path

        raise RuntimeError(
            f"TShark was not found at {configured_path}"
        )

    system_path = shutil.which("tshark")

    if system_path:
        return system_path

    known_paths = [
        WINDOWS_TSHARK_PATH,
        MAC_TSHARK_PATH,
        "/usr/bin/tshark",
        "/usr/local/bin/tshark",
    ]

    for path in known_paths:
        if Path(path).is_file():
            return path

    raise RuntimeError(
        "TShark could not be found. "
        "Install Wireshark/TShark or configure TSHARK_PATH."
    )


def list_capture_interfaces() -> list[CaptureInterface]:
    """Return capture interfaces reported by TShark."""

    tshark_path = get_tshark_path()

    try:
        result = subprocess.run(
            [tshark_path, "-D"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            "Timed out while listing capture interfaces."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "Unable to list capture interfaces."
        ) from exc

    interfaces: list[CaptureInterface] = []

    pattern = re.compile(
        r"^\s*(\d+)\.\s+(.+?)"
        r"(?:\s+\((.*)\))?\s*$"
    )

    for line in result.stdout.splitlines():
        match = pattern.match(line)

        if match is None:
            continue

        number, name, description = match.groups()

        interfaces.append(
            {
                "number": int(number),
                "name": name.strip(),
                "description": (
                    description.strip()
                    if description
                    else None
                ),
            }
        )

    if not interfaces:
        raise RuntimeError(
            "No capture interfaces were found."
        )

    return interfaces


def resolve_capture_interface(
    selector: str,
) -> str:
    """
    Resolve interface number, device name, or description.
    """

    selector = selector.strip()

    if not selector:
        raise ValueError(
            "Capture interface cannot be empty."
        )

    interfaces = list_capture_interfaces()
    normalized_selector = selector.casefold()

    for interface in interfaces:
        description = interface["description"]

        matches_number = (
            selector == str(interface["number"])
        )

        matches_name = (
            normalized_selector
            == interface["name"].casefold()
        )

        matches_description = (
            description is not None
            and normalized_selector
            == description.casefold()
        )

        if (
            matches_number
            or matches_name
            or matches_description
        ):
            return interface["name"]

    raise ValueError(
        f"Capture interface '{selector}' was not found."
    )