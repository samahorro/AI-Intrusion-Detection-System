
import { useEffect, useState } from "react";

import MetricCard from "../components/monitoring/MetricCard";
import ScanNetworkControl from "../components/monitoring/ScanNetworkControl";

import {
  captureService,
  type CaptureStats,
  type ExperimentalPredictionsResponse,
  type SecurityAlertsResponse,
} from "../services/captureService";

const formatBytes = (bytes: number) =>
  bytes < 1024
    ? `${bytes} B`
    : bytes < 1048576
      ? `${(bytes / 1024).toFixed(1)} KB`
      : `${(bytes / 1048576).toFixed(2)} MB`;

const formatTime = (stamp: string | null) => {
  if (!stamp) return "No packets yet";
  const date = new Date(stamp);
  return Number.isNaN(date.getTime())
    ? "Invalid timestamp"
    : date.toLocaleTimeString();
};

export default function Dashboard() {
  const [stats, setStats] = useState<CaptureStats | null>(null);
  const [error, setError] = useState("");

  const [predictions, setPredictions] =
    useState<ExperimentalPredictionsResponse | null>(null);

  const [predictionError, setPredictionError] = useState("");

  // KAN-253: Signature-based alert state.
  const [securityAlerts, setSecurityAlerts] =
    useState<SecurityAlertsResponse | null>(null);

  const [alertError, setAlertError] = useState("");
  const [alertsLoading, setAlertsLoading] = useState(true);

  // ==================================================
  // LIVE PACKET STATISTICS
  // ==================================================

  useEffect(() => {
    let active = true;
    let fetching = false;

    async function refresh() {
      if (fetching) return;
      fetching = true;

      try {
        const next = await captureService.getStats();

        if (active) {
          setStats(next);
          setError("");
        }
      } catch (err) {
        if (active) {
          setError(
            err instanceof Error
              ? err.message
              : "Unable to fetch statistics",
          );
        }
      } finally {
        fetching = false;
      }
    }

    void refresh();

    const timer = window.setInterval(
      () => void refresh(),
      2000,
    );

    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, []);

  // ==================================================
  // EXPERIMENTAL AI PREDICTIONS
  // ==================================================

  useEffect(() => {
    let active = true;
    let fetching = false;

    async function refreshPredictions() {
      if (fetching) return;
      fetching = true;

      try {
        const result =
          await captureService.getExperimentalPredictions();

        if (active) {
          setPredictions(result);
          setPredictionError("");
        }
      } catch (err) {
        if (active) {
          setPredictionError(
            err instanceof Error
              ? err.message
              : "Unable to fetch AI predictions",
          );
        }
      } finally {
        fetching = false;
      }
    }

    void refreshPredictions();

    const timer = window.setInterval(
      () => void refreshPredictions(),
      5000,
    );

    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, []);

  // ==================================================
  // KAN-253: LIVE SIGNATURE SECURITY ALERTS
  // ==================================================

  useEffect(() => {
    let active = true;
    let fetching = false;

    async function refreshAlerts() {
      if (fetching) return;
      fetching = true;

      try {
        const result =
          await captureService.getSecurityAlerts();

        if (active) {
          setSecurityAlerts(result);
          setAlertError("");
        }
      } catch (err) {
        if (active) {
          setSecurityAlerts(null);
          setAlertError(
            err instanceof Error
              ? err.message
              : "Unable to fetch security alerts",
          );
        }
      } finally {
        fetching = false;
        if (active) setAlertsLoading(false);
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

  // ==================================================
  // COMPUTED METRICS
  // ==================================================

  const protocols = stats?.protocols ?? {};
  const packets = stats?.packet_count ?? 0;

  const analyzedFlows = predictions?.prediction_count ?? 0;

  const predictedAttacks =
    predictions?.predictions.filter(
      (flow) => flow.ai_detection.prediction === "ATTACK",
    ).length ?? 0;

  const predictedBenign =
    predictions?.predictions.filter(
      (flow) => flow.ai_detection.prediction === "BENIGN",
    ).length ?? 0;

  const activeFlows = predictions?.active_flow_count ?? 0;

  const highestAttackScore = predictions?.predictions.length
    ? Math.max(
        ...predictions.predictions.map(
          (flow) => flow.ai_detection.attack_probability,
        ),
      )
    : null;

  const portScanAlerts =
    securityAlerts?.alerts.filter(
      (alert) => alert.attack_type === "port_scan",
    ).length ?? 0;

  return (
    <main className="page">
      <h1>AEGIS Dashboard</h1>

      {/* Monitoring status */}
      <section className="system-status">
        <h2>Monitoring Status</h2>

        <p>
          {error
            ? "Backend unreachable"
            : stats?.running
              ? "Monitoring is active"
              : "Monitoring is stopped"}
        </p>

        <p>Interface: {stats?.interface ?? "None"}</p>
      </section>

      {/* Network capture control */}
      <section>
        <h2>Network Scan</h2>
        <ScanNetworkControl />
      </section>

      {/* Backend errors */}
      {error && (
        <p role="alert" style={{ color: "red" }}>
          Backend error: {error}
        </p>
      )}

      {stats?.last_error && (
        <p role="alert" style={{ color: "red" }}>
          Capture error: {stats.last_error}
        </p>
      )}

      {/* Network metrics */}
      <section className="metrics-grid">
        <MetricCard
          title="Packets Captured"
          value={packets.toLocaleString()}
        />

        <MetricCard
          title="Data Captured"
          value={formatBytes(stats?.total_bytes ?? 0)}
        />

        <MetricCard
          title="Observed Source IPs"
          value={stats?.observed_source_ips ?? 0}
        />

        <MetricCard
          title="TCP Packets"
          value={protocols.TCP ?? 0}
        />

        <MetricCard
          title="UDP Packets"
          value={protocols.UDP ?? 0}
        />

        <MetricCard
          title="Last Packet"
          value={formatTime(stats?.last_packet_at ?? null)}
        />
      </section>

      {/* Protocol distribution */}
      <section>
        <h2>Protocol Distribution</h2>

        {packets === 0 ? (
          <p>No packets captured yet.</p>
        ) : (
          <div className="metrics-grid">
            {Object.entries(protocols).map(
              ([protocol, count]) => (
                <MetricCard
                  key={protocol}
                  title={protocol}
                  value={`${(
                    (count / packets) *
                    100
                  ).toFixed(1)}%`}
                />
              ),
            )}
          </div>
        )}
      </section>

      {/* Source IP information */}
      <section>
        <h2>Top Observed Source IPs</h2>

        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%" }}>
            <thead>
              <tr>
                <th align="left">Source IP</th>
                <th align="left">Packets</th>
              </tr>
            </thead>

            <tbody>
              {stats?.top_source_ips.map((item) => (
                <tr key={item.ip}>
                  <td>{item.ip}</td>
                  <td>{item.packets}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {!stats?.top_source_ips.length && (
          <p>No source IPs observed yet.</p>
        )}
      </section>

      {/* Recent captured packets */}
      <section>
        <h2>Recent Captured Packets</h2>

        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%" }}>
            <thead>
              <tr>
                <th align="left">Time</th>
                <th align="left">Source IP</th>
                <th align="left">Destination IP</th>
                <th align="left">Protocol</th>
                <th align="left">Bytes</th>
              </tr>
            </thead>

            <tbody>
              {stats?.recent_packets.map(
                (item, index) => (
                  <tr key={`${item.timestamp}-${index}`}>
                    <td>{formatTime(item.timestamp)}</td>
                    <td>{item.source_ip || "N/A"}</td>
                    <td>{item.destination_ip || "N/A"}</td>
                    <td>{item.protocol}</td>
                    <td>{item.length}</td>
                  </tr>
                ),
              )}
            </tbody>
          </table>
        </div>

        {!stats?.recent_packets.length && (
          <p>Start capture to view packet metadata.</p>
        )}
      </section>

      {/* ==================================================
          KAN-253: SIGNATURE-BASED SECURITY ALERTS
          ================================================== */}
      <section aria-labelledby="signature-alerts-heading">
        <h2 id="signature-alerts-heading">
          Signature-Based Security Alerts
        </h2>

        <p style={{ fontSize: "0.85rem", opacity: 0.8 }}>
          Automated port-scan detection using AEGIS
          signature rules. Alerts are separate from
          experimental AI model predictions.
        </p>

        <div className="metrics-grid">
          <MetricCard
            title="Security Alerts"
            value={
              alertError
                ? "Unavailable"
                : securityAlerts?.alert_count ?? "Loading"
            }
          />

          <MetricCard
            title="Port Scan Alerts"
            value={
              alertError
                ? "Unavailable"
                : securityAlerts
                  ? portScanAlerts
                  : "Loading"
            }
          />

          <MetricCard
            title="Capture Status"
            value={
              alertError
                ? "Unavailable"
                : securityAlerts
                  ? securityAlerts.capture_running
                    ? "Running"
                    : "Stopped"
                  : "Loading"
            }
          />
        </div>

        {alertError && (
          <p role="alert" style={{ color: "#dc2626" }}>
            Security alert error: {alertError}
          </p>
        )}

        {alertsLoading && !alertError && (
          <p>Loading security alerts...</p>
        )}

        {!alertsLoading &&
          !alertError &&
          securityAlerts?.alerts.length === 0 && (
            <p>
              No signature-based security alerts have
              been recorded in this capture session.
            </p>
          )}

        {!alertError &&
          securityAlerts &&
          securityAlerts.alerts.length > 0 && (
            <div style={{ overflowX: "auto", marginTop: 16 }}>
              <table style={{ width: "100%" }}>
                <thead>
                  <tr>
                    <th align="left">Time</th>
                    <th align="left">Detection</th>
                    <th align="left">Severity</th>
                    <th align="left">Source IP</th>
                    <th align="left">Destination IP</th>
                    <th align="left">Ports</th>
                    <th align="left">Rule ID</th>
                    <th align="left">Status</th>
                  </tr>
                </thead>

                <tbody>
                  {securityAlerts.alerts.map((alert, index) => (
                    <tr
                      key={`${alert.rule_id}-${alert.timestamp}-${index}`}
                    >
                      <td>{formatTime(alert.timestamp)}</td>
                      <td>
                        {alert.attack_type === "port_scan"
                          ? "Port Scan"
                          : alert.attack_type}
                      </td>
                      <td>
                        <strong
                          style={{
                            color:
                              alert.severity.toLowerCase() === "high"
                                ? "#dc2626"
                                : alert.severity.toLowerCase() === "medium"
                                  ? "#d97706"
                                  : "inherit",
                          }}
                        >
                          {alert.severity.toUpperCase()}
                        </strong>
                      </td>
                      <td>{alert.source_ip}</td>
                      <td>{alert.destination_ip}</td>
                      <td>{alert.ports_scanned}</td>
                      <td>{alert.rule_id}</td>
                      <td>{alert.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

        <p style={{ fontSize: "0.8rem", opacity: 0.7 }}>
          Alerts are retained in memory only and may be
          cleared when capture restarts or the backend
          restarts. Detections are not confirmed incidents.
        </p>
      </section>

      {/* Experimental AI Detection Overview */}
      <section>
        <h2>AI Threat Detection</h2>

        <p>
          AEGIS Random Forest v1 — Experimental
          Network Intrusion Detection
        </p>

        <p style={{ fontSize: "0.85rem", opacity: 0.8 }}>
          Model classifications are experimental.
          Live feature equivalence has not been verified,
          and automatic security alerts are disabled
          for AI predictions.
        </p>

        {predictionError && (
          <p role="alert" style={{ color: "#dc2626" }}>
            AI detection error: {predictionError}
          </p>
        )}

        <div className="metrics-grid">
          <MetricCard
            title="AI Analyzed Flows"
            value={analyzedFlows}
          />

          <MetricCard
            title="Predicted Benign"
            value={predictedBenign}
          />

          <MetricCard
            title="Predicted Attacks"
            value={predictedAttacks}
          />

          <MetricCard
            title="Active Network Flows"
            value={activeFlows}
          />

          <MetricCard
            title="Highest Attack Score"
            value={
              highestAttackScore === null
                ? "N/A"
                : `${(highestAttackScore * 100).toFixed(2)}%`
            }
          />

          <MetricCard
            title="Detection Mode"
            value="Experimental"
          />
        </div>

        <div style={{ marginTop: 16 }}>
          <p>
            <strong>Capture Status:</strong>{" "}
            {predictions
              ? predictions.capture_running
                ? "Running"
                : "Stopped"
              : "Loading"}
          </p>

          <p>
            <strong>Model:</strong>{" "}
            {predictions?.predictions[0]?.ai_detection.model_id ??
              "AEGIS Random Forest v1"}
          </p>

          <p>
            <strong>Security Alerts:</strong>{" "}
            {predictions?.alerts_enabled
              ? "Enabled"
              : "Disabled"}
          </p>

          <p>
            <strong>Live Feature Validation:</strong>{" "}
            {predictions?.live_feature_equivalence_verified
              ? "Verified"
              : "Not verified"}
          </p>
        </div>

        {!predictions && !predictionError && (
          <p>Loading AI detection statistics...</p>
        )}

        {predictions && analyzedFlows === 0 && (
          <p>
            No completed flows available.
            Start network capture to generate
            experimental AI predictions.
          </p>
        )}

        {predictions && analyzedFlows > 0 && (
          <p style={{ marginTop: 16 }}>
            AI predictions are available for the
            most recently completed network flows.
            Use the Security Console for detailed
            traffic investigation.
          </p>
        )}
      </section>
    </main>
  );
}
