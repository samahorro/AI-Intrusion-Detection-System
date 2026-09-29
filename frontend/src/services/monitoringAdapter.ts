import type {
  Alert,
  Device,
  SystemStatus,
} from "../types/monitoring";

export interface MonitoringApiResponse {
  system: {
    status: "online" | "offline" | "scanning";
    deviceCount: number;
    threatCount: number;
    blockedIpCount: number;
    activeAlertCount: number;
    onlineDeviceCount: number;
    lastScan: string;
  };
  devices: Device[];
  alerts: Alert[];
}

export interface MonitoringDashboardData {
  systemStatus: SystemStatus;
  devices: Device[];
  alerts: Alert[];
}

export function adaptMonitoringData(
  response: MonitoringApiResponse,
): MonitoringDashboardData {
  return {
    systemStatus: {
      status: response.system.status,
      devices: response.system.deviceCount,
      threats: response.system.threatCount,
      blockedIPs: response.system.blockedIpCount,
      activeAlerts: response.system.activeAlertCount,
      devicesOnline: response.system.onlineDeviceCount,
      lastScan: response.system.lastScan,
    },
    devices: response.devices,
    alerts: response.alerts,
  };
}

