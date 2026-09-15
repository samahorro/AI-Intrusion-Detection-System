import type {
  Alert,
  Device,
  SystemStatus,
} from "../types/monitoring";

export const systemStatus: SystemStatus = {
  status: "online",
  devices: 4,
  threats: 2,
  blockedIPs: 1,
};

export const alerts: Alert[] = [
  {
    id: 1,
    severity: "high",
    ip: "192.168.1.21",
    port: 22,
    attackType: "Port Scan",
    timestamp: "2026-09-14 18:45",
    confidence: 0.94,
  },
  {
    id: 2,
    severity: "medium",
    ip: "192.168.1.45",
    port: 443,
    attackType: "Suspicious Traffic",
    timestamp: "2026-09-14 18:52",
    confidence: 0.81,
  },
];

export const devices: Device[] = [
  {
    id: 1,
    ip: "192.168.1.10",
    hostname: "desktop-01",
    status: "online",
  },
  {
    id: 2,
    ip: "192.168.1.15",
    hostname: "server-01",
    status: "online",
  },
];