import { describe, expect, it } from "vitest";
import { adaptMonitoringData } from "./monitoringAdapter";

describe("adaptMonitoringData", () => {
  it("maps monitoring API data to dashboard data", () => {
    const response = {
      system: {
        status: "online" as const,
        deviceCount: 4,
        threatCount: 2,
        blockedIpCount: 1,
        activeAlertCount: 2,
        onlineDeviceCount: 3,
        lastScan: "2 minutes ago",
      },
      devices: [
        {
          id: 1,
          ip: "192.168.1.10",
          hostname: "desktop-01",
          status: "online" as const,
        },
      ],
      alerts: [
        {
          id: 1,
          severity: "high" as const,
          ip: "192.168.1.21",
          port: 22,
          attackType: "Port Scan",
          timestamp: "2026-09-14 18:45",
          confidence: 0.94,
        },
      ],
    };

    const result = adaptMonitoringData(response);

    expect(result.systemStatus).toEqual({
      status: "online",
      devices: 4,
      threats: 2,
      blockedIPs: 1,
      activeAlerts: 2,
      devicesOnline: 3,
      lastScan: "2 minutes ago",
    });

    expect(result.devices).toEqual(response.devices);
    expect(result.alerts).toEqual(response.alerts);
  });

  it("handles zero counts and empty arrays", () => {
    const response = {
      system: {
        status: "offline" as const,
        deviceCount: 0,
        threatCount: 0,
        blockedIpCount: 0,
        activeAlertCount: 0,
        onlineDeviceCount: 0,
        lastScan: "Never",
      },
      devices: [],
      alerts: [],
    };

    const result = adaptMonitoringData(response);

    expect(result.systemStatus.devices).toBe(0);
    expect(result.systemStatus.threats).toBe(0);
    expect(result.systemStatus.blockedIPs).toBe(0);
    expect(result.systemStatus.activeAlerts).toBe(0);
    expect(result.systemStatus.devicesOnline).toBe(0);
    expect(result.devices).toEqual([]);
    expect(result.alerts).toEqual([]);
  });
});