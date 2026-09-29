import type { MonitoringState } from "../../types/monitoring";

interface MonitoringStateDisplayProps {
  state: MonitoringState;
}

export default function MonitoringStateDisplay({
  state,
}: MonitoringStateDisplayProps) {
  const messages: Record<MonitoringState, string> = {
    idle: "Monitoring is idle",
    loading: "Loading monitoring data...",
    scanning: "Network scan in progress",
    monitoring: "Monitoring is active",
    error: "Monitoring encountered an error",
  };

  return (
    <div className={`monitoring-state monitoring-state-${state}`}>
      <strong>{state.toUpperCase()}</strong>
      <span>{messages[state]}</span>
    </div>
  );
}