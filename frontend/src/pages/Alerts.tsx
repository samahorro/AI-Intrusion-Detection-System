
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  captureService,
  type SecurityAlertsResponse,
} from "../services/captureService";

// ============================================================
// KAN-253: Signature-Based Security Alerts
// ============================================================

const formatTime = (timestamp: string | null | undefined) => {
  if (!timestamp) {
    return "Unavailable";
  }

  const date = new Date(timestamp);

  return Number.isNaN(date.getTime())
    ? "Invalid timestamp"
    : date.toLocaleString();
};

export default function Alerts() {
  const [data, setData] =
    useState<SecurityAlertsResponse | null>(null);

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  // ==========================================================
  // Retrieve real security alerts every 2 seconds
  // ==========================================================

  useEffect(() => {
    let active = true;
    let pending = false;

    async function refreshAlerts() {
      if (pending) {
        return;
      }

      pending = true;

      try {
        const response =
          await captureService.getSecurityAlerts();

        if (active) {
          setData(response);
          setError("");
        }
      } catch (err) {
        if (active) {
          setData(null);

          setError(
            err instanceof Error
              ? err.message
              : "Unable to retrieve security alerts",
          );
        }
      } finally {
        pending = false;

        if (active) {
          setLoading(false);
        }
      }
    }

    void refreshAlerts();

    const timer = window.setInterval(
      () => void refreshAlerts(),
      2000,
    );

    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, []);

  // ==========================================================
  // Security alert statistics
  // ==========================================================

  const alerts = data?.alerts ?? [];

  const portScanCount = alerts.filter(
    (alert) => alert.attack_type === "port_scan",
  ).length;

  // ==========================================================
  // AEGIS Alerts Dashboard
  // ==========================================================

  return (
    <main className="page">
      <h1>AEGIS Security Alerts</h1>

      <p>
        Automated signature-based intrusion detections
        generated from captured network traffic.
      </p>

      <p>
        <Link to="/console">
          Return to Security Console
        </Link>
      </p>

      {/* Security alert overview */}

      <section className="metrics-grid">
        <article className="alert-card">
          <h3>Total Security Alerts</h3>

          <strong>
            {error
              ? "Unavailable"
              : data
                ? data.alert_count
                : "Loading"}
          </strong>
        </article>

        <article className="alert-card">
          <h3>Port Scan Detections</h3>

          <strong>
            {error
              ? "Unavailable"
              : data
                ? portScanCount
                : "Loading"}
          </strong>
        </article>

        <article className="alert-card">
          <h3>Capture Status</h3>

          <strong>
            {error
              ? "Unavailable"
              : data
                ? data.capture_running
                  ? "Running"
                  : "Stopped"
                : "Loading"}
          </strong>
        </article>
      </section>

      {/* Alert retrieval errors */}

      {error && (
        <p role="alert" style={{ color: "#dc2626" }}>
          Security alert retrieval error: {error}
        </p>
      )}

      {/* Loading state */}

      {loading && !error && (
        <p>Loading security alerts...</p>
      )}

      {/* No detections */}

      {!loading && !error && alerts.length === 0 && (
        <p>
          No signature-based security alerts have been
          recorded during the current monitoring session.
        </p>
      )}

      {/* Real security alerts */}

      {!error && alerts.length > 0 && (
        <div className="alert-cards">
          {alerts.map((alert, index) => (
            <article
              className="alert-card"
              key={`${alert.rule_id}-${alert.timestamp}-${index}`}
            >
              <h3>
                {alert.attack_type === "port_scan"
                  ? "Port Scan Detected"
                  : alert.attack_type || "Unknown Event"}
              </h3>

              <p>
                <strong>Severity:</strong>{" "}
                {alert.severity || "Unavailable"}
              </p>

              <p>
                <strong>Source IP:</strong>{" "}
                {alert.source_ip || "Unavailable"}
              </p>

              <p>
                <strong>Destination IP:</strong>{" "}
                {alert.destination_ip || "Unavailable"}
              </p>

              <p>
                <strong>Distinct Ports Scanned:</strong>{" "}
                {alert.ports_scanned ?? "Unavailable"}
              </p>

              <p>
                <strong>Detection Rule:</strong>{" "}
                {alert.rule_id || "Unavailable"}
              </p>

              <p>
                <strong>Detected At:</strong>{" "}
                {formatTime(alert.timestamp)}
              </p>

              <p>
                <strong>Status:</strong>{" "}
                {alert.status || "Unavailable"}
              </p>

              <p>
                <strong>Detection Engine:</strong>{" "}
                Signature-Based IDS
              </p>
            </article>
          ))}
        </div>
      )}

      {/* Detection disclaimer */}

      <p style={{ marginTop: 24, opacity: 0.7 }}>
        Signature detections are not automatically
        confirmed security incidents. Alerts are
        currently stored in memory and may disappear
        when monitoring resets or the backend restarts.
      </p>
    </main>
  );
}
