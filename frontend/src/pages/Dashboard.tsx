import { useEffect, useState } from "react";
import MetricCard from "../components/monitoring/MetricCard";
import ScanNetworkControl from "../components/monitoring/ScanNetworkControl";
import { captureService, type CaptureStats } from "../services/captureService";

const formatBytes = (bytes: number) =>
  bytes < 1024
    ? `${bytes} B`
    : bytes < 1048576
      ? `${(bytes / 1024).toFixed(1)} KB`
      : `${(bytes / 1048576).toFixed(2)} MB`;
const formatTime = (stamp: string | null) =>
  stamp ? new Date(stamp).toLocaleTimeString() : "No packets yet";

export default function Dashboard() {
  const [stats, setStats] = useState<CaptureStats | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    let fetching = false;
    async function refresh() {
      if (fetching) return;
      fetching = true;
      try {
        const next = await captureService.getStats();
        if (active) {
          setStats(next);
          setError("");
        }
      } catch (err) {
        if (active)
          setError(
            err instanceof Error ? err.message : "Unable to fetch statistics",
          );
      } finally {
        fetching = false;
      }
    }
    void refresh();
    const timer = window.setInterval(() => void refresh(), 2000);
    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, []);

  const protocols = stats?.protocols ?? {};
  const packets = stats?.packet_count ?? 0;

  return (
    <main className="page">
      <h1>AI-IDS Dashboard</h1>
      <section className="system-status">
        <h2>Monitoring Status</h2>
        <p>
          {error
            ? "Backend unreachable"
            : stats?.running
              ? "Monitoring is active"
              : "Monitoring is stopped"}
        </p>
        <p>Interface: {stats?.interface ?? "None"}</p>
      </section>
      <section>
        <h2>Network Scan</h2>
        <ScanNetworkControl />
      </section>
      {error && (
        <p role="alert" style={{ color: "red" }}>
          Backend error: {error}
        </p>
      )}
      {stats?.last_error && (
        <p role="alert" style={{ color: "red" }}>
          Capture error: {stats.last_error}
        </p>
      )}
      <section className="metrics-grid">
        <MetricCard title="Packets Captured" value={packets.toLocaleString()} />
        <MetricCard
          title="Data Captured"
          value={formatBytes(stats?.total_bytes ?? 0)}
        />
        <MetricCard
          title="Observed Source IPs"
          value={stats?.observed_source_ips ?? 0}
        />
        <MetricCard title="TCP Packets" value={protocols.TCP ?? 0} />
        <MetricCard title="UDP Packets" value={protocols.UDP ?? 0} />
        <MetricCard
          title="Last Packet"
          value={formatTime(stats?.last_packet_at ?? null)}
        />
      </section>
      <section>
        <h2>Protocol Distribution</h2>
        {packets === 0 ? (
          <p>No packets captured yet.</p>
        ) : (
          <div className="metrics-grid">
            {Object.entries(protocols).map(([protocol, count]) => (
              <MetricCard
                key={protocol}
                title={protocol}
                value={`${((count / packets) * 100).toFixed(1)}%`}
              />
            ))}
          </div>
        )}
      </section>
      <section>
        <h2>Top Observed Source IPs</h2>
        <table style={{ width: "100%" }}>
          <thead>
            <tr>
              <th align="left">Source IP</th>
              <th align="left">Packets</th>
            </tr>
          </thead>
          <tbody>
            {stats?.top_source_ips.map((item) => (
              <tr key={item.ip}>
                <td>{item.ip}</td>
                <td>{item.packets}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {!stats?.top_source_ips.length && <p>No source IPs observed yet.</p>}
      </section>
      <section>
        <h2>Recent Captured Packets</h2>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%" }}>
            <thead>
              <tr>
                <th align="left">Time</th>
                <th align="left">Source IP</th>
                <th align="left">Destination IP</th>
                <th align="left">Protocol</th>
                <th align="left">Bytes</th>
              </tr>
            </thead>
            <tbody>
              {stats?.recent_packets.map((item, index) => (
                <tr key={`${item.timestamp}-${index}`}>
                  <td>{formatTime(item.timestamp)}</td>
                  <td>{item.source_ip || "N/A"}</td>
                  <td>{item.destination_ip || "N/A"}</td>
                  <td>{item.protocol}</td>
                  <td>{item.length}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {!stats?.recent_packets.length && (
          <p>Start capture to view packet metadata.</p>
        )}
      </section>
      <section>
        <h2>AI Threat Detection</h2>
        <p>
          Not connected to live traffic yet. Observed addresses and packet
          counts are not confirmed threats.
        </p>
      </section>
    </main>
  );
}
