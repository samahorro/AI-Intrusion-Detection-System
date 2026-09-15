import ThreatBadge from "../components/monitoring/ThreatBadge";
import { alerts } from "../data/mockData";

export default function Alerts() {
  return (
    <main className="page">
      <h1>Threat Alerts</h1>

      <div className="alert-cards">
        {alerts.map((alert) => (
          <article
            className="alert-card"
            key={alert.id}
          >
            <ThreatBadge severity={alert.severity} />

            <h3>{alert.attackType}</h3>

            <p>
              <strong>Source IP:</strong> {alert.ip}
            </p>

            <p>
              <strong>Port:</strong> {alert.port}
            </p>

            <p>
              <strong>Detected:</strong> {alert.timestamp}
            </p>

            <p>
              <strong>AI Confidence:</strong>{" "}
              {Math.round(alert.confidence * 100)}%
            </p>
          </article>
        ))}
      </div>
    </main>
  );
}