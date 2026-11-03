
"""Port-scan correlation for AEGIS SOC2-02 security validation."""

from collections import deque
from datetime import datetime, timezone
from ipaddress import ip_address
import math

from ml.detection.signature_detection import detect_signature
from ml.detection.signature_rules import PORT_SCAN_RULE


class PortScanTracker:
    """Detect distinct TCP SYN destination ports within a time window."""

    def __init__(self, window_seconds=60):
        if (
            isinstance(window_seconds, bool)
            or not isinstance(window_seconds, (int, float))
            or not math.isfinite(window_seconds)
            or window_seconds <= 0
        ):
            raise ValueError("window_seconds must be positive")

        self.window_seconds = window_seconds
        self._events = {}

    def reset(self):
        self._events.clear()

    def add_packet(self, packet):
        """Evaluate an already captured, normalized packet."""
        if not isinstance(packet, dict):
            raise ValueError("Packet must be a dictionary")

        if packet.get("protocol") != "TCP":
            return None

        if packet.get("tcp_syn") is not True:
            return None

        # SYN/ACK packets are responses, not new scan attempts.
        if packet.get("tcp_ack") is True:
            return None

        try:
            source = str(ip_address(packet["source_ip"]))
            destination = str(ip_address(packet["destination_ip"]))

            port = packet["destination_port"]
            if (
                isinstance(port, bool)
                or not isinstance(port, int)
                or not 1 <= port <= 65535
            ):
                raise ValueError("Invalid destination port")

            raw_time = packet["timestamp"]

            if isinstance(raw_time, str):
                timestamp = datetime.fromisoformat(
                    raw_time.replace("Z", "+00:00")
                ).timestamp()
            elif (
                isinstance(raw_time, (int, float))
                and not isinstance(raw_time, bool)
            ):
                timestamp = float(raw_time)
            else:
                raise ValueError("Invalid timestamp")

            if not math.isfinite(timestamp):
                raise ValueError("Invalid timestamp")

        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            raise ValueError("Invalid port-scan packet") from exc

        key = (source, destination)
        events = self._events.setdefault(key, deque())

        # Keep the sliding window based on packet event timestamps.
        while events and timestamp - events[0][0] > self.window_seconds:
            events.popleft()

        events.append((timestamp, port))

        unique_ports = len({destination_port for _, destination_port in events})

        signature = detect_signature({
            "ports_scanned": unique_ports
        })

        if not signature["detected"]:
            return None

        if signature["attack_type"] != "port_scan":
            return None

        return {
            **signature,
            "rule_id": PORT_SCAN_RULE.rule_id,
            "source_ip": source,
            "destination_ip": destination,
            "ports_scanned": unique_ports,
            "timestamp": datetime.fromtimestamp(
                timestamp, tz=timezone.utc
            ).isoformat(),
        }
