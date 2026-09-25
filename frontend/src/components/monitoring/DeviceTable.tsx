import type { Device } from "../../types/monitoring";
import StatusBadge from "./StatusBadge";

interface DeviceTableProps {
  devices: Device[];
}

export default function DeviceTable({
  devices,
}: DeviceTableProps) {
  if (devices.length === 0) {
    return (
      <div className="device-table-empty">
        No monitored devices found.
      </div>
    );
  }

  return (
    <div className="device-table-wrapper">
      <table className="device-table">
        <thead>
          <tr>
            <th>Hostname</th>
            <th>IP Address</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
          {devices.map((device) => (
            <tr key={device.id}>
              <td>{device.hostname}</td>
              <td>{device.ip}</td>
              <td>
                <StatusBadge status={device.status} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}