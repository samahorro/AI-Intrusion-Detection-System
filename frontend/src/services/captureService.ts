
import { reportSessionExpiry } from "./auth/sessionExpiryEvents";
import { resolveApiBaseUrl } from "./apiBaseUrl";

const API_URL = resolveApiBaseUrl(
  import.meta.env.VITE_API_URL,
  import.meta.env.VITE_API_BASE_URL,
);

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
// Signature-Based Detection Alert Types
// ============================================================

/**
 * Signature alert produced by the backend detection pipeline.
 *
 * These fields describe the anticipated /capture/alerts
 * response and should be verified against the backend schema.
 */
export type SignatureAlert = {
  event_type: string;
  attack_type: string;
  severity: "normal" | "low" | "medium" | "high";
  detected: boolean;
  reason: string;
  rule_id: string;
  source_ip: string;
  destination_ip: string;
  ports_scanned: number;
  timestamp: string;
  status: string;
};

/**
 * Response from the live signature-alert endpoint.
 *
 * Backend endpoint:
 * GET /capture/alerts
 */
export type SignatureAlertsResponse = {
  status: string;
  capture_running: boolean;
  alert_count: number;
  alerts: SignatureAlert[];
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

    // The experimental prediction API is not implemented in the
    // current backend. Do not invent AI results or silently
    // replace them with mocks.
    if (
      response.status === 404 &&
      path === "/capture/experimental-predictions"
    ) {
      throw new Error(
        "Experimental AI predictions are unavailable on this backend (HTTP 404). The backend/ML integration is still pending.",
      );
    }

    // Keep signature alert failures visible rather than
    // displaying fabricated detection results.
    if (
      response.status === 404 &&
      path === "/capture/alerts"
    ) {
      throw new Error(
        "Live signature alerts are unavailable on this backend (HTTP 404).",
      );
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
  // ==========================================================
  // Network Interfaces
  // ==========================================================

  // Retrieve available network interfaces
  async getInterfaces() {
    return apiRequest<{ interfaces: CaptureInterface[] }>(
      "/capture/interfaces",
    );
  },

  // ==========================================================
  // Packet Capture Status and Statistics
  // ==========================================================

  // Get current packet capture status
  async getStatus() {
    return apiRequest<CaptureStatus>(
      "/capture/status",
    );
  },

  // Get live packet capture statistics
  async getStats() {
    return apiRequest<CaptureStats>(
      "/capture/stats",
    );
  },

  // Start packet capture on a selected interface
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

  // Stop packet capture
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

  // ==========================================================
  // Live Signature-Based Intrusion Detection Alerts
  // ==========================================================

  /**
   * Retrieve real signature-based intrusion alerts from
   * the backend capture and detection pipeline.
   *
   * Backend endpoint:
   * GET /capture/alerts
   *
   * The dashboard will use this method to retrieve and
   * display available security alerts.
   *
   * This method does not generate mock alerts.
   */
  async getSignatureAlerts() {
    return apiRequest<SignatureAlertsResponse>(
      "/capture/alerts",
    );
  },
};
