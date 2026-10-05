import os
import subprocess
from typing import Any

DEFAULT_TSHARK_PATH = (
    "/Applications/Wireshark.app/Contents/MacOS/tshark"
)


def capture_packets(
    interface: str = "en0",
    packet_count: int = 50,
) -> list[dict[str, Any]]:
    """
    Capture network packet metadata using TShark.

    Packet payload contents are not captured. Only metadata required
    for IDS flow processing is returned.
    """

    if packet_count <= 0:
        raise ValueError(
            "packet_count must be greater than zero"
        )

    if not interface.strip():
        raise ValueError(
            "interface cannot be empty"
        )

    tshark_path = os.getenv(
        "TSHARK_PATH",
        DEFAULT_TSHARK_PATH,
    )

    command = [
        tshark_path,
        "-i",
        interface,
        "-c",
        str(packet_count),
        "-T",
        "fields",
        "-E",
        "separator=|",
        "-E",
        "occurrence=f",
        "-e",
        "frame.time_epoch",
        "-e",
        "ip.src",
        "-e",
        "ip.dst",
        "-e",
        "frame.len",
        "-e",
        "tcp.srcport",
        "-e",
        "tcp.dstport",
        "-e",
        "udp.srcport",
        "-e",
        "udp.dstport",
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            f"TShark was not found at {tshark_path}"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            "TShark capture timed out"
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"TShark capture failed: {exc.stderr.strip()}"
        ) from exc

    packets: list[dict[str, Any]] = []

    for line in result.stdout.splitlines():
        fields = line.split("|")

        if len(fields) != 8:
            continue

        (
            timestamp,
            source_ip,
            destination_ip,
            frame_length,
            tcp_source_port,
            tcp_destination_port,
            udp_source_port,
            udp_destination_port,
        ) = fields

        if (
            not timestamp
            or not source_ip
            or not destination_ip
            or not frame_length
        ):
            continue

        try:
            parsed_timestamp = float(timestamp)
            parsed_length = int(frame_length)
        except ValueError:
            continue

        source_port = (
            tcp_source_port
            or udp_source_port
            or None
        )

        destination_port = (
            tcp_destination_port
            or udp_destination_port
            or None
        )

        packets.append(
            {
                "timestamp": parsed_timestamp,
                "source_ip": source_ip,
                "destination_ip": destination_ip,
                "source_port": (
                    int(source_port)
                    if source_port
                    else None
                ),
                "destination_port": (
                    int(destination_port)
                    if destination_port
                    else None
                ),
                "length": parsed_length,
            }
        )

    return packets