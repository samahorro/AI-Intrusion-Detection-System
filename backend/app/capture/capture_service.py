import subprocess

from .interface_service import (
    get_tshark_path,
    resolve_capture_interface,
)


class CaptureService:
    """Manage a running TShark packet capture process."""

    def __init__(self):
        self.process: subprocess.Popen[str] | None = None
        self.interface: str | None = None

    def is_running(self) -> bool:
        """Return whether a capture process is currently active."""

        return (
            self.process is not None
            and self.process.poll() is None
        )

    def _build_command(
        self,
        interface: str,
    ) -> list[str]:
        """Build the TShark command used for live capture."""

        tshark_path = get_tshark_path()

        return [
            tshark_path,
            "-i",
            interface,
            "-l",
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

    def start(
        self,
        interface_selector: str,
    ) -> dict[str, str]:
        """Start packet capture on the selected interface."""

        if self.is_running():
            raise RuntimeError(
                "Packet capture is already running."
            )

        resolved_interface = (
            resolve_capture_interface(
                interface_selector
            )
        )

        command = self._build_command(
            resolved_interface
        )

        try:
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
        except OSError as exc:
            self.process = None

            raise RuntimeError(
                "Unable to start packet capture."
            ) from exc

        self.interface = resolved_interface

        return {
            "status": "running",
            "interface": resolved_interface,
        }

    def stop(self) -> dict[str, str]:
        """Stop the active packet capture process."""

        if not self.is_running():
            self.process = None
            self.interface = None

            raise RuntimeError(
                "Packet capture is not running."
            )

        assert self.process is not None

        process = self.process

        process.terminate()

        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)

        stopped_interface = self.interface

        self.process = None
        self.interface = None

        return {
            "status": "stopped",
            "interface": stopped_interface or "",
        }


capture_service = CaptureService()