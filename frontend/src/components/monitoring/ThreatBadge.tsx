import type { ThreatSeverity } from "../../types/monitoring";

interface ThreatBadgeProps {
  severity: ThreatSeverity;
}

export default function ThreatBadge({
  severity,
}: ThreatBadgeProps) {
  return (
    <span className={`threat-badge ${severity}`}>
      {severity.toUpperCase()}
    </span>
  );
}