
import { useEffect, useState } from "react";

import {
  captureService,
  type SignatureAlert,
} from "../services/captureService";

// ============================================================
// FORMAT DETECTION TIMESTAMP
// ============================================================

function formatAlertTime(timestamp: string): string {
  const date = new Date(timestamp);

  if (Number.isNaN(date.getTime())) {
    return timestamp;
  }

  return date.toLocaleString();
}

// ============================================================
// FORMAT ATTACK TYPE
// ============================================================

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
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase(),
    );
}

// ============================================================
// SEVERITY COLORS
// ============================================================

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

// ============================================================
// FORMAT DETECTION METHOD
// ============================================================

function formatDetectionMethod(
  method?: string,
): string {
  switch (method) {
    case "signature":
      return "Signature-based";

    case "ml":
      return "Machine Learning";

    case "combined":
      return "Combined Detection";

    default:
      return "Not available";
  }
}

// ============================================================
// VALIDATE THREAT SCORE
// ============================================================

function getThreatScore(
  score?: number,
): number | null {
  if (
    typeof score !== "number" ||
    !Number.isFinite(score)
  ) {
    return null;
  }

  return Math.max(0, Math.min(100, score));
}

// ============================================================
// LIVE SIGNATURE ALERTS PANEL
// ============================================================

export default function SignatureAlertsPanel() {
  const [alerts, setAlerts] = useState<
    SignatureAlert[]
  >([]);

  const [captureRunning, setCaptureRunning] =
    useState(false);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");

  // ==========================================================
  // FETCH LIVE SIGNATURE ALERTS
  // ==========================================================

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
        setCaptureRunning(
          response.capture_running,
        );
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

    // Initial request.
    void fetchSignatureAlerts();

    // Refresh the alert list every two seconds.
    const interval = window.setInterval(() => {
      void fetchSignatureAlerts();
    }, 2000);

    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, []);

  // ==========================================================
  // RENDER LIVE ALERTS PANEL
  // ==========================================================

  return (
    <section
      className="sentinel-panel"
      aria-label="Live Signature Alerts"
      style={{
        marginBottom: "20px",
      }}
    >
      {/* ======================================================
          PANEL HEADER
      ====================================================== */}

      <div className="sentinel-panel-head">
        <div>
          <h2>Live Signature Alerts</h2>

          <p>
            Real-time signature detection,
            threat scoring, and security alerts
          </p>
        </div>

        <span className="sentinel-panel-tag">
          AUTO-REFRESH • 2S
        </span>
      </div>

      {/* ======================================================
          PANEL CONTENT
      ====================================================== */}

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
              color: captureRunning
                ? "#5eead4"
                : "#94a3b8",
            }}
          >
            {captureRunning
              ? "● Network capture active"
              : "○ Network capture stopped"}
          </span>

          <span
            style={{
              fontSize: "13px",
              fontWeight: 600,
              color: "#cbd5e1",
            }}
          >
            {alerts.length} signature{" "}
            {alerts.length === 1
              ? "alert"
              : "alerts"}
          </span>
        </div>

        {/* ====================================================
            LOADING STATE
        ==================================================== */}

        {loading && (
          <p
            className="sentinel-empty"
            role="status"
          >
            Loading signature alerts...
          </p>
        )}

        {/* ====================================================
            API ERROR STATE
        ==================================================== */}

        {!loading && error && (
          <div
            role="alert"
            style={{
              padding: "14px",
              borderRadius: "8px",
              background:
                "rgba(239,68,68,0.08)",
              border:
                "1px solid rgba(239,68,68,0.3)",
              color: "#f87171",
            }}
          >
            Unable to load signature alerts:{" "}
            {error}
          </div>
        )}

        {/* ====================================================
            EMPTY ALERT STATE
        ==================================================== */}

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

        {/* ====================================================
            LIVE SIGNATURE ALERT CARDS
        ==================================================== */}

        {!loading &&
          !error &&
          alerts.length > 0 && (
            <div
              style={{
                display: "grid",
                gap: "14px",
              }}
            >
              {alerts
                .slice(0, 20)
                .map((alert, index) => {
                  const severity =
                    alert.classification ??
                    alert.severity;

                  const severityColor =
                    getSeverityColor(severity);

                  const threatScore =
                    getThreatScore(
                      alert.threat_score,
                    );

                  return (
                    <article
                      key={`${alert.timestamp}-${alert.source_ip}-${alert.destination_ip}-${alert.rule_id}-${index}`}
                      style={{
                        padding: "18px",
                        borderRadius: "12px",
                        background:
                          "linear-gradient(135deg, rgba(28,20,65,0.88), rgba(15,12,37,0.95))",
                        border:
                          "1px solid rgba(164,123,224,0.2)",
                        borderLeft:
                          `4px solid ${severityColor}`,
                        boxShadow:
                          "0 12px 32px rgba(0,0,0,0.15)",
                      }}
                    >
                      {/* ======================================
                          ALERT TITLE AND SEVERITY
                      ====================================== */}

                      <div
                        style={{
                          display: "flex",
                          justifyContent:
                            "space-between",
                          alignItems: "center",
                          flexWrap: "wrap",
                          gap: "12px",
                          marginBottom: "16px",
                        }}
                      >
                        <div>
                          <strong
                            style={{
                              display: "block",
                              fontSize: "16px",
                              color: "#f5f3ff",
                              marginBottom: "5px",
                            }}
                          >
                            {formatAttackType(
                              alert.attack_type,
                            )}
                          </strong>

                          <span
                            style={{
                              fontSize: "12px",
                              color: "#a5a0c6",
                            }}
                          >
                            Rule: {alert.rule_id}
                          </span>
                        </div>

                        <span
                          style={{
                            padding: "6px 11px",
                            borderRadius: "7px",
                            background:
                              `${severityColor}18`,
                            border:
                              `1px solid ${severityColor}40`,
                            color: severityColor,
                            fontSize: "11px",
                            fontWeight: 800,
                            letterSpacing: "0.05em",
                            textTransform:
                              "uppercase",
                          }}
                        >
                          {severity}
                        </span>
                      </div>

                      {/* ======================================
                          SPRINT 5 THREAT SCORE
                      ====================================== */}

                      <div
                        style={{
                          padding: "16px",
                          borderRadius: "10px",
                          marginBottom: "18px",
                          background:
                            "rgba(13,10,34,0.7)",
                          border:
                            "1px solid rgba(164,123,224,0.16)",
                        }}
                      >
                        <div
                          style={{
                            display: "flex",
                            justifyContent:
                              "space-between",
                            alignItems:
                              "flex-start",
                            flexWrap: "wrap",
                            gap: "14px",
                            marginBottom: "12px",
                          }}
                        >
                          {/* Numerical threat score */}

                          <div>
                            <div
                              style={{
                                fontSize: "11px",
                                color: "#a5a0c6",
                                fontWeight: 800,
                                letterSpacing:
                                  "0.1em",
                                marginBottom: "6px",
                              }}
                            >
                              THREAT SCORE
                            </div>

                            <div
                              style={{
                                display: "flex",
                                alignItems:
                                  "baseline",
                                gap: "5px",
                              }}
                            >
                              <strong
                                style={{
                                  fontSize: "30px",
                                  color:
                                    severityColor,
                                  lineHeight: 1,
                                }}
                              >
                                {threatScore === null
                                  ? "N/A"
                                  : threatScore}
                              </strong>

                              {threatScore !== null && (
                                <span
                                  style={{
                                    fontSize: "13px",
                                    color: "#a5a0c6",
                                  }}
                                >
                                  / 100
                                </span>
                              )}
                            </div>
                          </div>

                          {/* Threat classification */}

                          <div
                            style={{
                              textAlign: "right",
                            }}
                          >
                            <div
                              style={{
                                fontSize: "11px",
                                fontWeight: 800,
                                color: "#a5a0c6",
                                letterSpacing:
                                  "0.1em",
                                marginBottom: "8px",
                              }}
                            >
                              CLASSIFICATION
                            </div>

                            <strong
                              style={{
                                color:
                                  severityColor,
                                fontSize: "13px",
                                textTransform:
                                  "uppercase",
                              }}
                            >
                              {severity}
                            </strong>
                          </div>
                        </div>

                        {/* Threat score progress bar */}

                        <div
                          role={
                            threatScore === null
                              ? undefined
                              : "progressbar"
                          }
                          aria-label={
                            threatScore === null
                              ? undefined
                              : "Threat score"
                          }
                          aria-valuemin={
                            threatScore === null
                              ? undefined
                              : 0
                          }
                          aria-valuemax={
                            threatScore === null
                              ? undefined
                              : 100
                          }
                          aria-valuenow={
                            threatScore === null
                              ? undefined
                              : threatScore
                          }
                          style={{
                            width: "100%",
                            height: "8px",
                            borderRadius: "999px",
                            background:
                              "rgba(148,163,184,0.18)",
                            overflow: "hidden",
                            marginBottom: "12px",
                          }}
                        >
                          <div
                            style={{
                              width: `${threatScore ?? 0}%`,
                              height: "100%",
                              borderRadius: "999px",
                              background:
                                severityColor,
                              transition:
                                "width 0.3s ease",
                            }}
                          />
                        </div>

                        {/* Detection method */}

                        <div
                          style={{
                            display: "flex",
                            justifyContent:
                              "space-between",
                            alignItems: "center",
                            flexWrap: "wrap",
                            gap: "8px",
                          }}
                        >
                          <span
                            style={{
                              fontSize: "12px",
                              color: "#a5a0c6",
                            }}
                          >
                            Detection Method
                          </span>

                          <span
                            style={{
                              color: "#d8c9ff",
                              fontSize: "12px",
                              fontWeight: 600,
                            }}
                          >
                            {formatDetectionMethod(
                              alert.detection_method,
                            )}
                          </span>
                        </div>
                      </div>

                      {/* ======================================
                          NETWORK AND DETECTION DETAILS
                      ====================================== */}

                      <div
                        style={{
                          display: "grid",
                          gridTemplateColumns:
                            "repeat(auto-fit, minmax(180px, 1fr))",
                          gap: "14px",
                          fontSize: "13px",
                          marginBottom: "16px",
                        }}
                      >
                        <div>
                          <div
                            style={{
                              color: "#a5a0c6",
                              fontSize: "11px",
                              marginBottom: "5px",
                            }}
                          >
                            SOURCE IP
                          </div>

                          <strong
                            style={{
                              color: "#f5f3ff",
                              overflowWrap:
                                "anywhere",
                            }}
                          >
                            {alert.source_ip}
                          </strong>
                        </div>

                        <div>
                          <div
                            style={{
                              color: "#a5a0c6",
                              fontSize: "11px",
                              marginBottom: "5px",
                            }}
                          >
                            DESTINATION IP
                          </div>

                          <strong
                            style={{
                              color: "#f5f3ff",
                              overflowWrap:
                                "anywhere",
                            }}
                          >
                            {alert.destination_ip}
                          </strong>
                        </div>

                        <div>
                          <div
                            style={{
                              color: "#a5a0c6",
                              fontSize: "11px",
                              marginBottom: "5px",
                            }}
                          >
                            PORTS SCANNED
                          </div>

                          <strong
                            style={{
                              color: "#f5f3ff",
                            }}
                          >
                            {alert.ports_scanned}
                          </strong>
                        </div>

                        <div>
                          <div
                            style={{
                              color: "#a5a0c6",
                              fontSize: "11px",
                              marginBottom: "5px",
                            }}
                          >
                            DETECTED AT
                          </div>

                          <strong
                            style={{
                              color: "#f5f3ff",
                            }}
                          >
                            {formatAlertTime(
                              alert.timestamp,
                            )}
                          </strong>
                        </div>
                      </div>

                      {/* ======================================
                          REASON FOR DETECTION
                      ====================================== */}

                      <div
                        style={{
                          padding: "13px 14px",
                          borderRadius: "8px",
                          background:
                            "rgba(139,92,246,0.08)",
                          border:
                            "1px solid rgba(139,92,246,0.15)",
                          marginBottom: "12px",
                        }}
                      >
                        <div
                          style={{
                            fontSize: "11px",
                            fontWeight: 800,
                            letterSpacing:
                              "0.08em",
                            color: "#c4a5ff",
                            marginBottom: "7px",
                          }}
                        >
                          DETECTION REASON
                        </div>

                        <p
                          style={{
                            margin: 0,
                            color: "#cbd5e1",
                            fontSize: "13px",
                            lineHeight: 1.6,
                          }}
                        >
                          {alert.reason}
                        </p>
                      </div>

                      {/* ======================================
                          ALERT STATUS
                      ====================================== */}

                      <div
                        style={{
                          display: "flex",
                          justifyContent:
                            "space-between",
                          alignItems: "center",
                          gap: "12px",
                          flexWrap: "wrap",
                          fontSize: "12px",
                        }}
                      >
                        <span
                          style={{
                            color: "#a5a0c6",
                          }}
                        >
                          Status:{" "}
                          <strong
                            style={{
                              color: "#d8c9ff",
                              textTransform:
                                "capitalize",
                            }}
                          >
                            {alert.status}
                          </strong>
                        </span>

                        <span
                          style={{
                            color: "#8b83a9",
                          }}
                        >
                          {alert.event_type ===
                          "signature_detection"
                            ? "Signature Detection Event"
                            : alert.event_type}
                        </span>
                      </div>
                    </article>
                  );
                })}
            </div>
          )}
      </div>
    </section>
  );
}
