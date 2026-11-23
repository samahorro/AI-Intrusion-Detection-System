
import { useEffect, useState } from "react";

import {
  captureService,
  type SignatureAlert,
} from "../services/captureService";

// --------------------------------------------------
// FORMAT DETECTION TIMESTAMP
// --------------------------------------------------

function formatAlertTime(timestamp: string): string {
  const date = new Date(timestamp);

  if (Number.isNaN(date.getTime())) {
    return timestamp;
  }

  return date.toLocaleString();
}

// --------------------------------------------------
// FORMAT ATTACK TYPE
// --------------------------------------------------

function formatAttackType(
  attackType: string | null,
): string {
  if (attackType === "port_scan") {
    return "Port Scan Detected";
  }

  if (attackType === "brute_force") {
    return "Brute Force Detected";
  }

  if (!attackType) {
    return "Signature Detection";
  }

  return attackType
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

// --------------------------------------------------
// SEVERITY COLOR
// --------------------------------------------------

function getSeverityColor(severity: string): string {
  switch (severity.toLowerCase()) {
    case "high":
      return "#ef4444";

    case "medium":
      return "#f59e0b";

    case "low":
      return "#38bdf8";

    default:
      return "#94a3b8";
  }
}

// --------------------------------------------------
// LIVE SIGNATURE ALERTS PANEL
// --------------------------------------------------

export default function SignatureAlertsPanel() {
  const [alerts, setAlerts] = useState<
    SignatureAlert[]
  >([]);

  const [captureRunning, setCaptureRunning] =
    useState(false);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");

  // ------------------------------------------------
  // FETCH LIVE SIGNATURE ALERTS
  // ------------------------------------------------

  useEffect(() => {
    let active = true;
    let requestPending = false;

    async function fetchSignatureAlerts() {
      if (requestPending) {
        return;
      }

      requestPending = true;

      try {
        const response =
          await captureService.getSignatureAlerts();

        if (!active) {
          return;
        }

        setAlerts(response.alerts);
        setCaptureRunning(response.capture_running);
        setError("");
      } catch (err) {
        if (!active) {
          return;
        }

        setError(
          err instanceof Error
            ? err.message
            : "Unable to retrieve signature alerts.",
        );
      } finally {
        requestPending = false;

        if (active) {
          setLoading(false);
        }
      }
    }

    // Fetch immediately when the component mounts.
    void fetchSignatureAlerts();

    // Automatically refresh every 2 seconds.
    const interval = window.setInterval(() => {
      void fetchSignatureAlerts();
    }, 2000);

    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, []);

  // ------------------------------------------------
  // RENDER LIVE ALERT PANEL
  // ------------------------------------------------

  return (
    <section
      className="sentinel-panel"
      aria-label="Live Signature Alerts"
      style={{ marginBottom: "20px" }}
    >
      {/* Panel header */}

      <div className="sentinel-panel-head">
        <div>
          <h2>Live Signature Alerts</h2>

          <p>
            Signature-based threats detected from
            captured network traffic
          </p>
        </div>

        <span className="sentinel-panel-tag">
          AUTO-REFRESH • 2S
        </span>
      </div>

      {/* Panel content */}

      <div style={{ padding: "20px" }}>
        {/* Monitoring status */}

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: "12px",
            flexWrap: "wrap",
            marginBottom: "18px",
          }}
        >
          <span
            style={{
              fontSize: "13px",
              color: "#94a3b8",
            }}
          >
            {captureRunning
              ? "Network capture active"
              : "Network capture stopped"}
          </span>

          <span
            style={{
              fontSize: "13px",
              fontWeight: 600,
            }}
          >
            {alerts.length} signature alerts
          </span>
        </div>

        {/* Loading state */}

        {loading && (
          <p className="sentinel-empty" role="status">
            Loading signature alerts...
          </p>
        )}

        {/* API error state */}

        {!loading && error && (
          <div
            role="alert"
            style={{
              padding: "14px",
              borderRadius: "8px",
              background: "rgba(239,68,68,0.08)",
              border: "1px solid rgba(239,68,68,0.3)",
              color: "#f87171",
            }}
          >
            Unable to load signature alerts: {error}
          </div>
        )}

        {/* No alerts detected */}

        {!loading &&
          !error &&
          alerts.length === 0 && (
            <div
              className="sentinel-empty"
              style={{
                padding: "24px",
                textAlign: "center",
              }}
            >
              <p
                style={{
                  fontWeight: 600,
                  marginBottom: "8px",
                }}
              >
                No Signature Alerts Detected
              </p>

              <p>
                {captureRunning
                  ? "Monitoring network traffic for suspicious activity."
                  : "Start network capture to monitor for signature-based threats."}
              </p>
            </div>
          )}

        {/* Live signature alert cards */}

        {!loading &&
          !error &&
          alerts.length > 0 && (
            <div
              style={{
                display: "grid",
                gap: "12px",
              }}
            >
              {alerts.slice(0, 20).map(
                (alert, index) => {
                  const severityColor =
                    getSeverityColor(
                      alert.severity,
                    );

                  return (
                    <article
                      key={`${alert.timestamp}-${alert.source_ip}-${alert.destination_ip}-${alert.rule_id}-${index}`}
                      style={{
                        padding: "16px",
                        borderRadius: "10px",
                        background:
                          "rgba(15,23,42,0.35)",
                        border:
                          "1px solid rgba(148,163,184,0.15)",
                        borderLeft:
                          `4px solid ${severityColor}`,
                      }}
                    >
                      {/* Alert title and severity */}

                      <div
                        style={{
                          display: "flex",
                          justifyContent:
                            "space-between",
                          alignItems: "center",
                          flexWrap: "wrap",
                          gap: "12px",
                          marginBottom: "12px",
                        }}
                      >
                        <strong
                          style={{
                            fontSize: "15px",
                          }}
                        >
                          {formatAttackType(
                            alert.attack_type,
                          )}
                        </strong>

                        <span
                          style={{
                            padding: "5px 10px",
                            borderRadius: "6px",
                            background:
                              `${severityColor}18`,
                            color: severityColor,
                            fontSize: "12px",
                            fontWeight: 700,
                            textTransform:
                              "uppercase",
                          }}
                        >
                          {alert.severity}
                        </span>
                      </div>

                      {/* Alert details */}

                      <div
                        style={{
                          display: "grid",
                          gap: "8px",
                          fontSize: "13px",
                          color: "#cbd5e1",
                        }}
                      >
                        <div>
                          <strong>Source IP: </strong>
                          {alert.source_ip}
                        </div>

                        <div>
                          <strong>Destination IP: </strong>
                          {alert.destination_ip}
                        </div>

                        <div>
                          <strong>Ports Scanned: </strong>
                          {alert.ports_scanned}
                        </div>

                        <div>
                          <strong>Detection Rule: </strong>
                          {alert.rule_id}
                        </div>

                        <div>
                          <strong>Reason: </strong>
                          {alert.reason}
                        </div>

                        <div>
                          <strong>Detected At: </strong>
                          {formatAlertTime(
                            alert.timestamp,
                          )}
                        </div>

                        <div>
                          <strong>Status: </strong>
                          {alert.status}
                        </div>
                      </div>
                    </article>
                  );
                },
              )}
            </div>
          )}
      </div>
    </section>
  );
}
