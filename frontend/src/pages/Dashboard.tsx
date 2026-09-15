import MetricCard from "../components/monitoring/MetricCard";
import StatusBadge from "../components/monitoring/StatusBadge";
import ThreatBadge from "../components/monitoring/ThreatBadge";
import {
  alerts,
  systemStatus,
} from "../data/mockData";

export default function Dashboard() {
  return (
    <main className="page">
      <h1>AI-IDS Dashboard</h1>

      <section className="system-status">
        <h2>System Status</h2>
        <StatusBadge status={systemStatus.status} />
      </section>

      <section className="metrics-grid">
        <MetricCard
          title="Devices"
          value={systemStatus.devices}
        />
        <MetricCard
          title="Threats"
          value={systemStatus.threats}
        />
        <MetricCard
          title="Blocked IPs"
          value={systemStatus.blockedIPs}
        />
      </section>

      <section>
        <h2>Recent Alerts</h2>

        <div className="alerts-list">
          {alerts.map((alert) => (
            <div
              className="alert-row"
              key={alert.id}
            >
              <ThreatBadge severity={alert.severity} />
              <span>{alert.ip}</span>
              <span>{alert.attackType}</span>
              <span>
                {Math.round(alert.confidence * 100)}%
              </span>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}