import ThreatBadge from "../components/monitoring/ThreatBadge";
import { alerts as defaultAlerts } from "../data/mockData";
import type { Alert } from "../types/monitoring";

type DisplayAlert = Partial<Alert> & Pick<Alert, "id">;

type AlertsProps = {
  alerts?: DisplayAlert[];
};

export default function Alerts({
  alerts = defaultAlerts,
}: AlertsProps) {
  return (
    <main className="page">
      <h1>Threat Alerts</h1>

      {alerts.length === 0 ? (
        <p>No security alerts available.</p>
      ) : (
        <div className="alert-cards">
          {alerts.map((alert) => (
            <article
              className="alert-card"
              key={alert.id}
            >
              {alert.severity ? (
                <ThreatBadge severity={alert.severity} />
              ) : (
                <p>Severity: Unavailable</p>
              )}

              <h3>{alert.attackType || "Unknown Event"}</h3>

              <p>
                <strong>Source IP:</strong>{" "}
                {alert.ip || "Unavailable"}
              </p>

              <p>
                <strong>Port:</strong>{" "}
                {alert.port ?? "Unavailable"}
              </p>

              <p>
                <strong>Detected:</strong>{" "}
                {alert.timestamp || "Unavailable"}
              </p>

              <p>
                <strong>AI Confidence:</strong>{" "}
                {typeof alert.confidence === "number" &&
                Number.isFinite(alert.confidence) &&
                alert.confidence >= 0 &&
                alert.confidence <= 1
                  ? `${Math.round(alert.confidence * 100)}%`
                  : "Unavailable"}
              </p>
            </article>
          ))}
        </div>
      )}
    </main>
  );
}