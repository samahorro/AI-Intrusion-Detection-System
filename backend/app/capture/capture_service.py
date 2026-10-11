"""Live TShark capture and bounded, in-memory packet statistics."""
import subprocess
import threading
from collections import Counter, deque
from datetime import UTC, datetime

from .flow_bridge import FlowBridge
from .interface_service import get_tshark_path, resolve_capture_interface


class CaptureService:
    def __init__(self):
        self.process = None
        self.interface = None
        self._lock = threading.RLock()
        self._generation = 0
        self.flow_bridge = FlowBridge()
        self._reset_stats()

    def _reset_stats(self):
        self.packet_count = 0
        self.total_bytes = 0
        self.protocols = Counter()
        self.source_ips = Counter()
        self.recent_packets = deque(maxlen=25)
        self.last_packet_at = None
        self.last_error = None

    def is_running(self):
        with self._lock:
            return self.process is not None and self.process.poll() is None

    def _build_command(self, interface):
        return [
            get_tshark_path(), "-i", interface, "-l", "-n",
            "-T", "fields", "-E", "separator=|", "-E", "occurrence=f",
            "-e", "frame.time_epoch", "-e", "ip.src", "-e", "ipv6.src",
            "-e", "ip.dst", "-e", "ipv6.dst", "-e", "frame.len",
            "-e", "tcp.srcport", "-e", "tcp.dstport",
            "-e", "udp.srcport", "-e", "udp.dstport",
        ]

    def start(self, interface_selector):
        with self._lock:
            if self.is_running():
                raise RuntimeError("Packet capture is already running.")
            interface = resolve_capture_interface(interface_selector)
            command = self._build_command(interface)
            try:
                process = subprocess.Popen(
                    command, stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL, text=True, encoding="utf-8",
                    errors="replace", bufsize=1,
                )
            except OSError as exc:
                raise RuntimeError("Unable to start packet capture.") from exc
            self._generation += 1
            generation = self._generation
            self.process = process
            self.interface = interface
            self._reset_stats()
            self.flow_bridge.reset()
            if process.stdout is not None:
                threading.Thread(
                    target=self._read_packets, args=(process, generation),
                    daemon=True, name="tshark-packet-reader",
                ).start()
            return {"status": "running", "interface": interface}

    def _read_packets(self, process, generation):
        try:
            for line in process.stdout:
                parts = line.rstrip("\r\n").split("|")
                if len(parts) != 10:
                    continue
                (epoch, src4, src6, dst4, dst6, size,
                 tcp_source, tcp_dest, udp_source, udp_dest) = parts
                try:
                    length = int(size)
                    timestamp = datetime.fromtimestamp(
                        float(epoch), tz=UTC
                    ).isoformat()
                except (ValueError, OverflowError, OSError):
                    continue
                if tcp_source or tcp_dest:
                    protocol = "TCP"
                elif udp_source or udp_dest:
                    protocol = "UDP"
                else:
                    protocol = "OTHER"
                source = src4 or src6
                packet = {
                    "timestamp": timestamp,
                    "source_ip": source,
                    "destination_ip": dst4 or dst6,
                    "protocol": protocol,
                    "length": length,
                    "source_port": tcp_source or udp_source or None,
                    "destination_port": tcp_dest or udp_dest or None,
                }
                with self._lock:
                    if generation != self._generation:
                        break
                    self.packet_count += 1
                    self.total_bytes += length
                    self.protocols[protocol] += 1
                    if source:
                        self.source_ips[source] += 1
                    self.recent_packets.appendleft(packet)
                    self.flow_bridge.add_packet(packet)
                    self.last_packet_at = timestamp
        except (OSError, UnicodeError) as exc:
            with self._lock:
                if generation == self._generation:
                    self.last_error = str(exc)
        finally:
            if process.stdout is not None:
                process.stdout.close()

    def get_stats(self):
        with self._lock:
            return {
                "running": self.is_running(),
                "interface": self.interface if self.is_running() else None,
                "packet_count": self.packet_count,
                "total_bytes": self.total_bytes,
                "observed_source_ips": len(self.source_ips),
                "protocols": dict(self.protocols),
                "top_source_ips": [
                    {"ip": ip, "packets": count}
                    for ip, count in self.source_ips.most_common(10)
                ],
                "recent_packets": list(self.recent_packets),
                "last_packet_at": self.last_packet_at,
                "last_error": self.last_error,
            }

    def stop(self):
        with self._lock:
            if not self.is_running():
                raise RuntimeError("Packet capture is not running.")
            process = self.process
            stopped_interface = self.interface
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            self._generation += 1
            self.process = None
            self.interface = None
            return {"status": "stopped", "interface": stopped_interface or ""}


capture_service = CaptureService()
