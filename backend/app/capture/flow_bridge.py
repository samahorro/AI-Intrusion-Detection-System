
"""Bridge between live TShark packets and experimental IDS flows.

Provides:
- Packet validation and normalization
- Flow tracking and ML feature preparation
- Signature-based port-scan detection
- Bounded, in-memory security alerts
"""

import math
import time
from collections import deque
from datetime import datetime
from threading import RLock

from backend.app.capture.flow_aggregator import (
    FlowTracker,
    aggregate_packets,
)

from ml.preprocessing.flow_preprocessor import (
    REQUIRED_FEATURES,
    preprocess_flow,
)

from ml.detection.port_scan_tracker import PortScanTracker


class FlowBridge:
    def __init__(
        self,
        max_packets=2000,
        max_completed=200,
    ):
        # Existing packet and flow tracking.
        self._packets = deque(maxlen=max_packets)
        self._completed = deque(maxlen=max_completed)
        self._tracker = FlowTracker()

        # Signature-based intrusion detection.
        self._scan_tracker = PortScanTracker(window_seconds=60)

        # Bounded alert history.
        self._alerts = deque(maxlen=200)

        # Alert deduplication history:
        # (timestamp, source_ip, destination_ip).
        self._alert_times = deque(maxlen=200)

        # Thread-safe access to shared state.
        self._lock = RLock()

    # ==================================================
    # RESET CAPTURE AND DETECTION STATE
    # ==================================================

    def reset(self):
        """Clear packet, flow, and security-detection state."""

        with self._lock:
            self._packets.clear()
            self._completed.clear()
            self._tracker.reset()

            self._scan_tracker.reset()
            self._alerts.clear()
            self._alert_times.clear()

    # ==================================================
    # PREPARE FLOWS FOR EXPERIMENTAL AI/ML
    # ==================================================

    def _prepare_flow(self, result):
        """Validate and prepare completed network-flow features."""

        features = result["flow"]

        if any(
            key not in features
            or isinstance(features[key], bool)
            or not isinstance(features[key], (int, float))
            or not math.isfinite(features[key])
            or features[key] < 0
            for key in REQUIRED_FEATURES
        ):
            return None

        return {
            "protocol": result.get("protocol"),
            "source_ip": result["source_ip"],
            "destination_ip": result["destination_ip"],
            "source_port": result["source_port"],
            "destination_port": result["destination_port"],
            "packet_count": result["packet_count"],
            "total_bytes": result["total_bytes"],
            "completion_reason": result.get(
                "completion_reason"
            ),
            "features": features,
            "feature_vector": preprocess_flow(features),
        }

    def _store_completed(self, results):
        """Store validated completed flows."""

        for result in results:
            prepared = self._prepare_flow(result)

            if prepared is not None:
                self._completed.append(prepared)

    # ==================================================
    # SIGNATURE-BASED PORT-SCAN DETECTION
    # ==================================================

    def _evaluate_port_scan(self, packet):
        """Evaluate TCP SYN traffic and generate deduplicated alerts.

        Called while the FlowBridge lock is held.
        """

        # Only TCP packets can contribute to TCP port scans.
        if packet.get("protocol") != "TCP":
            return

        # The SYN flag must explicitly be True.
        if packet.get("tcp_syn") is not True:
            return

        # Missing ACK information must not be interpreted
        # as proof that ACK is False.
        if packet.get("tcp_ack") is not False:
            return

        try:
            detection = self._scan_tracker.add_packet(packet)

        except ValueError:
            # Malformed network data must not crash
            # the live packet-processing pipeline.
            return

        if detection is None:
            return

        timestamp = packet["timestamp"]

        source_ip = detection["source_ip"]
        destination_ip = detection["destination_ip"]

        # Prevent repeated alerts for the same source and
        # destination during the 60-second suppression window.
        for (
            previous_time,
            previous_source,
            previous_destination,
        ) in self._alert_times:

            if (
                previous_source != source_ip
                or previous_destination != destination_ip
            ):
                continue

            elapsed = timestamp - previous_time

            if 0 <= elapsed < 60:
                return

        # Structured signature-based security alert.
        alert = {
            **detection,
            "event_type": "signature_detection",
            "status": "new",
        }

        self._alerts.append(alert)

        self._alert_times.append(
            (
                timestamp,
                source_ip,
                destination_ip,
            )
        )

    # ==================================================
    # RECEIVE AND PROCESS LIVE PACKETS
    # ==================================================

    def add_packet(self, packet):
        """Receive one packet from the live capture service."""

        if not isinstance(packet, dict):
            return False

        if packet.get("protocol") not in ("TCP", "UDP"):
            return False

        if (
            not packet.get("source_ip")
            or not packet.get("destination_ip")
        ):
            return False

        try:
            timestamp = datetime.fromisoformat(
                packet["timestamp"]
            ).timestamp()

            if isinstance(packet["length"], bool):
                return False

            length = int(packet["length"])

            if (
                isinstance(packet["source_port"], bool)
                or isinstance(packet["destination_port"], bool)
            ):
                return False

            src_port = int(packet["source_port"])
            dst_port = int(packet["destination_port"])

        except (
            KeyError,
            TypeError,
            ValueError,
            OverflowError,
        ):
            return False

        if (
            not math.isfinite(timestamp)
            or length < 0
            or not (0 <= src_port <= 65535)
            or not (0 <= dst_port <= 65535)
        ):
            return False

        # Preserve TCP flag values from the capture service.
        # None means that a flag was not supplied.
        normalized = {
            "timestamp": timestamp,
            "source_ip": packet["source_ip"],
            "destination_ip": packet["destination_ip"],
            "source_port": src_port,
            "destination_port": dst_port,
            "protocol": packet["protocol"],
            "length": length,
            "tcp_syn": packet.get("tcp_syn"),
            "tcp_ack": packet.get("tcp_ack"),
            "tcp_fin": packet.get("tcp_fin", False),
            "tcp_rst": packet.get("tcp_rst", False),
        }

        with self._lock:
            # Preserve existing packet history.
            self._packets.append(normalized)

            # Preserve existing experimental flow tracking.
            completed = self._tracker.add_packet(normalized)
            self._store_completed(completed)

            # Evaluate captured packets for port scanning.
            self._evaluate_port_scan(normalized)

        return True

    # ==================================================
    # EXPIRE IDLE NETWORK FLOWS
    # ==================================================

    def expire_flows(self):
        """Expire idle flows even when no new packets arrive."""

        with self._lock:
            completed = self._tracker.expire_flows(
                time.time()
            )

            self._store_completed(completed)

            return len(completed)

    # ==================================================
    # FLUSH ACTIVE NETWORK FLOWS
    # ==================================================

    def flush(self):
        """Finalize active flows when capture stops."""

        with self._lock:
            completed = self._tracker.flush()

            self._store_completed(completed)

            return len(completed)

    # ==================================================
    # GET COMPLETED NETWORK FLOWS
    # ==================================================

    def get_completed_flows(self):
        """Return experimental completed-flow records."""

        self.expire_flows()

        with self._lock:
            return list(self._completed)

    # ==================================================
    # GET SECURITY ALERTS
    # ==================================================

    def get_alerts(self):
        """Return generated security alerts, newest first."""

        with self._lock:
            return list(reversed(self._alerts))

    # ==================================================
    # GET FLOW PREVIEW AND MONITORING STATUS
    # ==================================================

    def snapshot(self):
        """Return live packet and experimental flow statistics.

        Preserve the original preview API while exposing
        experimental flow-tracking status.
        """

        self.expire_flows()

        with self._lock:
            packets = list(self._packets)

            active_count = self._tracker.active_count()

            completed = list(self._completed)

        by_protocol = {}

        for packet in packets:
            by_protocol.setdefault(
                packet["protocol"], []
            ).append(packet)

        flows = []

        for protocol, group in by_protocol.items():
            for result in aggregate_packets(group):
                result["protocol"] = protocol

                prepared = self._prepare_flow(result)

                if prepared is not None:
                    flows.append(prepared)

        return {
            "status": "preview_only",
            "window_packets": len(packets),
            "feature_order": list(REQUIRED_FEATURES),
            "flow_count": len(flows),
            "flows": flows[:100],
            "experimental_tracking": {
                "active_flow_count": active_count,
                "completed_flow_count": len(completed),
                "completed_flows": completed[-100:],
                "live_feature_equivalence_verified": False,
            },
        }
