"""Development-stage bridge: captured packet metadata -> flow -> ML feature vector.

The sliding bounded window is NOT a production flow/session tracker. Protocol is
kept separate; current repository's aggregate_packets() keys only on endpoints.
"""
from collections import deque
from datetime import datetime
from threading import RLock
import math
from backend.app.capture.flow_aggregator import aggregate_packets
from ml.preprocessing.flow_preprocessor import REQUIRED_FEATURES, preprocess_flow


class FlowBridge:
    def __init__(self, max_packets=2000):
        self._packets = deque(maxlen=max_packets)
        self._lock = RLock()

    def reset(self):
        with self._lock:
            self._packets.clear()

    def add_packet(self, packet):
        """Accept packet shape produced by the current live CaptureService."""
        if packet.get("protocol") not in ("TCP", "UDP"):
            return False
        if not packet.get("source_ip") or not packet.get("destination_ip"):
            return False
        try:
            timestamp = datetime.fromisoformat(packet["timestamp"]).timestamp()
            length = int(packet["length"])
            src_port = int(packet["source_port"])
            dst_port = int(packet["destination_port"])
        except (KeyError, TypeError, ValueError, OverflowError):
            return False
        if not math.isfinite(timestamp) or length < 0 or not (0 <= src_port <= 65535 and 0 <= dst_port <= 65535):
            return False
        normalized = {
            "timestamp": timestamp,
            "source_ip": packet["source_ip"],
            "destination_ip": packet["destination_ip"],
            "source_port": src_port,
            "destination_port": dst_port,
            "protocol": packet["protocol"],
            "length": length,
        }
        with self._lock:
            self._packets.append(normalized)
        return True

    def snapshot(self):
        """Read-only preview of recent flows, NOT completed connections/predictions."""
        with self._lock:
            packets = list(self._packets)
        by_protocol = {}
        for packet in packets:
            by_protocol.setdefault(packet["protocol"], []).append(packet)
        flows = []
        for protocol, group in by_protocol.items():
            for result in aggregate_packets(group):
                features = result["flow"]
                # Do not use the preprocessor's missing-feature zero fallback here.
                if any(key not in features or not isinstance(features[key], (int, float))
                       or not math.isfinite(features[key]) for key in REQUIRED_FEATURES):
                    continue
                flows.append({
                    "protocol": protocol,
                    "source_ip": result["source_ip"],
                    "destination_ip": result["destination_ip"],
                    "source_port": result["source_port"],
                    "destination_port": result["destination_port"],
                    "packet_count": result["packet_count"],
                    "total_bytes": result["total_bytes"],
                    "features": features,
                    "feature_vector": preprocess_flow(features),
                })
        return {"status": "preview_only", "window_packets": len(packets),
                "feature_order": list(REQUIRED_FEATURES), "flow_count": len(flows),
                "flows": flows[:100]}
