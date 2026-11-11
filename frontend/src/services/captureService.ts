
import { reportSessionExpiry } from "./auth/sessionExpiryEvents";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

// ============================================================
// Network Interface Types
// ============================================================

export type CaptureInterface = {
  number: number;
  name: string;
  description: string | null;
};

export type CaptureStatus = {
  running: boolean;
  interface: string | null;
};

// ============================================================
// Packet Capture Types
// ============================================================

export type LivePacket = {
  timestamp: string;
  source_ip: string;
  destination_ip: string;
  protocol: string;
  length: number;
  source_port: string | null;
  destination_port: string | null;
  tcp_syn?: boolean;
  tcp_ack?: boolean;
  tcp_fin?: boolean;
  tcp_rst?: boolean;
};

export type SourceIPStats = {
  ip: string;
  packets: number;
};

export type CaptureStats = {
  running: boolean;
  interface: string | null;
  packet_count: number;
  total_bytes: number;
  observed_source_ips: number;
  protocols: Record<string, number>;
  top_source_ips: SourceIPStats[];
  recent_packets: LivePacket[];
  last_packet_at: string | null;
  last_error: string | null;
};

// ============================================================
// Experimental AI Detection Types
// ============================================================

export type AIDetectionResult = {
  prediction: "BENIGN" | "ATTACK";
  prediction_value: 0 | 1;
  attack_probability: number;
  threshold: number;
  model_id: string;
};

export type ExperimentalFlowPrediction = {
  source_ip: string;
  destination_ip: string;
  source_port: number | null;
  destination_port: number | null;
  protocol: string;
  packet_count: number;
  completion_reason: string | null;
  features: Record<string, number>;
  ai_detection: AIDetectionResult;
};

export type ExperimentalPredictionsResponse = {
  status: "experimental";
  capture_running: boolean;
  live_feature_equivalence_verified: boolean;
  alerts_enabled: boolean;
  active_flow_count: number;
  prediction_count: number;
  predictions: ExperimentalFlowPrediction[];
};

// ============================================================
// KAN-253: Signature-Based Security Alert Types
// ============================================================

export type SignatureSecurityAlert = {
  detected: boolean;
  rule_id: string;
  attack_type: string;
  severity: string;
  source_ip: string;
  destination_ip: string;
  ports_scanned: number;
  timestamp: string;
  reason?: string;
  event_type: "signature_detection";
  status: string;
};

export type SecurityAlertsResponse = {
  status: "ok";
  capture_running: boolean;
  alert_count: number;
  alerts: SignatureSecurityAlert[];
};

// ============================================================
// API Request Helper
// ============================================================

async function apiRequest<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    credentials: "include",
  });

  if (!response.ok) {
    if (response.status === 401) {
      reportSessionExpiry();
    }
    // The experimental prediction API is not implemented in the current
    // backend. Do not invent AI results or silently replace them with mocks.
    if (response.status === 404 && path === "/capture/experimental-predictions") {
      throw new Error("Experimental AI predictions are unavailable on this backend (HTTP 404). The backend/ML integration is still pending.");
    }
    const error = await response.json().catch(() => null);

    throw new Error(
      typeof error?.detail === "string"
        ? error.detail
        : `Request failed: ${response.status}`,
    );
  }

  return response.json() as Promise<T>;
}

// ============================================================
// Capture Service
// ============================================================

export const captureService = {
  // Retrieve available network interfaces.
  async getInterfaces() {
    return apiRequest<{ interfaces: CaptureInterface[] }>(
      "/capture/interfaces",
    );
  },

  // Get current packet capture status.
  async getStatus() {
    return apiRequest<CaptureStatus>(
      "/capture/status",
    );
  },

  // Get live packet capture statistics.
  async getStats() {
    return apiRequest<CaptureStats>(
      "/capture/stats",
    );
  },

  // ==========================================================
  // KAN-253: Retrieve Signature-Based Security Alerts
  // ==========================================================

  /**
   * Retrieve automated signature-based intrusion alerts.
   *
   * Backend endpoint:
   * GET /capture/alerts
   *
   * The request uses the existing authenticated session.
   * Results are from PortScanTracker and FlowBridge.
   * They are not experimental AI predictions.
   */
  async getSecurityAlerts() {
    return apiRequest<SecurityAlertsResponse>(
      "/capture/alerts",
    );
  },

  // ==========================================================
  // Network Capture Controls
  // ==========================================================

  // Start packet capture on a selected interface.
  async start(interfaceName: string) {
    return apiRequest("/capture/start", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        interface: interfaceName,
      }),
    });
  },

  // Stop packet capture.
  async stop() {
    return apiRequest("/capture/stop", {
      method: "POST",
    });
  },

  // ==========================================================
  // AEGIS Experimental AI Detection
  // ==========================================================

  /**
   * Retrieve experimental AI predictions for completed
   * TCP/UDP network flows.
   *
   * Backend endpoint:
   * GET /capture/experimental-predictions
   *
   * Predictions are generated by the trained CICIDS2017
   * Random Forest classifier.
   *
   * Results are experimental and do not represent
   * verified security incidents.
   */
  async getExperimentalPredictions() {
    return apiRequest<ExperimentalPredictionsResponse>(
      "/capture/experimental-predictions",
    );
  },
};
