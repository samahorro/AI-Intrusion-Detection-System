export type ThreatSeverity =
  | "low"
  | "medium"
  | "high"
  | "critical";

export type SystemState =
  | "online"
  | "offline"
  | "scanning";

export interface SystemStatus {
  status: SystemState;
  devices: number;
  threats: number;
  blockedIPs: number;
}

export interface Alert {
  id: number;
  severity: ThreatSeverity;
  ip: string;
  port: number;
  attackType: string;
  timestamp: string;
  confidence: number;
}

export interface Device {
  id: number;
  ip: string;
  hostname: string;
  status: "online" | "offline";
}