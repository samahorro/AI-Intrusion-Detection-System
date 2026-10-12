import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { captureService, type CaptureInterface, type CaptureStats } from "../services/captureService";
import "./SecurityConsole.css";

const bytesLabel = (value: number) => value < 1024 ? `${value} B` : value < 1048576 ? `${(value / 1024).toFixed(1)} KB` : `${(value / 1048576).toFixed(2)} MB`;
const timeLabel = (value: string | null | undefined) => value ? new Date(value).toLocaleTimeString() : "—";

export default function SecurityConsole() {
  const [stats, setStats] = useState<CaptureStats | null>(null);
  const [interfaces, setInterfaces] = useState<CaptureInterface[]>([]);
  const [selectedInterface, setSelectedInterface] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [refreshAt, setRefreshAt] = useState("");
  const [filter, setFilter] = useState("");
  const [tab, setTab] = useState<"traffic" | "hosts">("traffic");

  useEffect(() => {
    let active = true;
    let pending = false;
    async function refresh() {
      if (pending) return;
      pending = true;
      try {
        const next = await captureService.getStats();
        if (active) {
          setStats(next);
          setRefreshAt(new Date().toLocaleTimeString());
          setError("");
        }
      } catch (e) {
        if (active) setError(e instanceof Error ? e.message : "Failed to fetch live statistics");
      } finally {
        pending = false;
      }
    }
    async function initialize() {
      try {
        const result = await captureService.getInterfaces();
        if (!active) return;
        setInterfaces(result.interfaces);
        const wifi = result.interfaces.find((item) => item.description?.includes("Wi-Fi") || item.name === "Wi-Fi");
        setSelectedInterface(wifi?.name ?? result.interfaces[0]?.name ?? "");
      } catch (e) {
        if (active) setError(e instanceof Error ? e.message : "Cannot list interfaces");
      }
    }
    void initialize();
    void refresh();
    const timer = window.setInterval(() => void refresh(), 2000);
    return () => { active = false; window.clearInterval(timer); };
  }, []);

  async function toggleCapture() {
    if (busy) return;
    setBusy(true);
    setError("");
    try {
      if (stats?.running) await captureService.stop();
      else {
        if (!selectedInterface) throw new Error("Select a network interface first");
        await captureService.start(selectedInterface);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Capture command failed");
    } finally {
      try { setStats(await captureService.getStats()); }
      catch { setError("Unable to verify capture status"); }
      setBusy(false);
    }
  }

  const packets = stats?.packet_count ?? 0;
  const protocols = useMemo(() => Object.entries(stats?.protocols ?? {}).sort((a,b)=>b[1]-a[1]), [stats]);
  const query = filter.trim().toLowerCase();
  const recentPackets = (stats?.recent_packets ?? []).filter((p) =>
    `${p.source_ip} ${p.destination_ip} ${p.protocol} ${p.source_port ?? ""} ${p.destination_port ?? ""}`.toLowerCase().includes(query)
  );
  const observedHosts = (stats?.top_source_ips ?? []).filter((h) => h.ip.toLowerCase().includes(query));

  return (
    <div className="sentinel-console">
      <aside className="sentinel-sidebar">
        <div className="sentinel-brand"><span className="sentinel-brand-logo">◈</span><span>AEGIS<span className="sentinel-brand-accent"> / IDS</span><small>NETWORK DEFENSE CONSOLE</small></span></div>
        <div className="sentinel-nav-label">WORKSPACE</div>
        <div className="sentinel-nav-selected">▦ <span>Security overview</span></div>
        <button className="sentinel-nav-link" onClick={() => setTab("traffic")}>≋ <span>Network traffic</span></button>
        <button className="sentinel-nav-link" onClick={() => setTab("hosts")}>▧ <span>Observed hosts</span></button>
        <div className="sentinel-nav-label sentinel-section-space">DETECTION</div>
        <div className="sentinel-nav-muted">◇ <span>AI detections <i>Coming soon</i></span></div>
        <div className="sentinel-nav-muted">▤ <span>Incident alerts <i>Coming soon</i></span></div>
        <div className="sentinel-nav-foot"><Link to="/dashboard">← Original dashboard</Link><span>Live telemetry • Local session</span></div>
      </aside>
      <main className="sentinel-main">
        <header className="sentinel-topbar"><div><span className="sentinel-breadcrumb">SECURITY OPERATIONS</span> <span className="sentinel-slash">/</span> Overview</div><div className="sentinel-topright"><span className="sentinel-live-dot"/> LIVE API <span className="sentinel-separator">|</span> {refreshAt || "Connecting..."}</div></header>
        <div className="sentinel-content">
          <div className="sentinel-heading"><div><div className="sentinel-eyebrow">NETWORK VISIBILITY</div><h1>Security Overview</h1><p>Real-time packet telemetry from your monitored network interface</p></div><div className={`sentinel-state ${stats?.running ? "is-running" : ""}`}><span className="sentinel-state-dot"/>{error ? "Backend error" : stats?.running ? "Capture active" : "Capture stopped"}</div></div>
          {error && <div className="sentinel-error" role="alert">Connection error: {error}</div>}
          {stats?.last_error && <div className="sentinel-error" role="alert">TShark: {stats.last_error}</div>}
          <section className="sentinel-capture-bar" aria-label="Capture controls"><div><div className="sentinel-control-label">MONITORING INTERFACE</div><select aria-label="Capture interface" disabled={busy || Boolean(stats?.running)} value={stats?.running ? stats.interface ?? selectedInterface : selectedInterface} onChange={(e) => setSelectedInterface(e.target.value)}><option value="">Select interface</option>{interfaces.map((item) => <option key={item.name} value={item.name}>{item.description || item.name}</option>)}</select></div><div className="sentinel-capture-actions"><span className="sentinel-capture-hint">{stats?.running ? "Packets are being captured" : "Ready to monitor"}</span><button onClick={() => void toggleCapture()} disabled={busy || (!stats?.running && !selectedInterface)} className={`sentinel-capture-button ${stats?.running ? "is-stop" : ""}`}>{busy ? "Working..." : stats?.running ? "■ Stop capture" : "▶ Start capture"}</button></div></section>
          <section className="sentinel-metrics" aria-label="Live network metrics">
            <div className="sentinel-metric"><span>TOTAL PACKETS</span><strong>{packets.toLocaleString()}</strong><small>Current capture session</small><b>↗</b></div>
            <div className="sentinel-metric"><span>DATA OBSERVED</span><strong>{bytesLabel(stats?.total_bytes ?? 0)}</strong><small>Captured frame bytes</small><b>◫</b></div>
            <div className="sentinel-metric"><span>UNIQUE SOURCE IPS</span><strong>{(stats?.observed_source_ips ?? 0).toLocaleString()}</strong><small>Not necessarily devices</small><b>⌘</b></div>
            <div className="sentinel-metric"><span>LAST PACKET</span><strong className="sentinel-metric-time">{timeLabel(stats?.last_packet_at)}</strong><small>Local time</small><b>◷</b></div>
          </section>
          <div className="sentinel-panels">
            <section className="sentinel-panel"><div className="sentinel-panel-head"><div><h2>Protocol distribution</h2><p>Traffic by transport protocol</p></div><span className="sentinel-panel-tag">LIVE</span></div>{packets ? <div className="sentinel-protocols">{protocols.map(([name, count], index) => <div className="sentinel-protocol" key={name}><div><span className={`sentinel-protocol-square square-${index % 4}`}/><strong>{name}</strong><span>{count.toLocaleString()} packets</span><em>{(100*count/packets).toFixed(1)}%</em></div><div className="sentinel-protocol-track"><div className={`sentinel-protocol-fill fill-${index % 4}`} style={{width:`${100*count/packets}%`}}/></div></div>)}</div> : <p className="sentinel-empty">Start capture to see protocol activity.</p>}</section>
            <section className="sentinel-panel"><div className="sentinel-panel-head"><div><h2>Detection engine</h2><p>AI analysis and signature matching</p></div><span className="sentinel-panel-tag muted">NOT CONNECTED</span></div><div className="sentinel-detection-empty"><div className="sentinel-detection-icon">◇</div><strong>Detection integration pending</strong><p>Packet capture is live. Network flow aggregation and ML inference have not yet been connected to this telemetry stream.</p><div>NO THREAT CLAIMS FROM RAW TRAFFIC</div></div></section>
          </div>
          <section className="sentinel-panel sentinel-activity"><div className="sentinel-panel-head"><div><h2>Network activity</h2><p>Latest captured packets and observed source addresses</p></div><span className="sentinel-panel-tag">AUTO-REFRESH • 2S</span></div><div className="sentinel-table-tools"><div className="sentinel-tabs"><button className={tab === "traffic" ? "active" : ""} onClick={() => setTab("traffic")}>Packet activity</button><button className={tab === "hosts" ? "active" : ""} onClick={() => setTab("hosts")}>Observed sources</button></div><input aria-label="Filter traffic or addresses" placeholder="Filter IP, protocol, or port..." value={filter} onChange={(e) => setFilter(e.target.value)}/></div><div className="sentinel-table-wrap">{tab === "traffic" ? <table><thead><tr><th>TIME</th><th>SOURCE IP</th><th>DESTINATION IP</th><th>PROTOCOL</th><th>BYTES</th></tr></thead><tbody>{recentPackets.length ? recentPackets.map((p,index) => <tr key={`${p.timestamp}-${index}`}><td>{timeLabel(p.timestamp)}</td><td className="sentinel-mono">{p.source_ip || "—"}</td><td className="sentinel-mono">{p.destination_ip || "—"}</td><td><span className="sentinel-proto-chip">{p.protocol}</span></td><td>{p.length.toLocaleString()}</td></tr>) : <tr><td className="sentinel-table-empty" colSpan={5}>No matching packets captured yet</td></tr>}</tbody></table> : <table><thead><tr><th>SOURCE IP</th><th>PACKETS OBSERVED</th><th>VISIBILITY</th></tr></thead><tbody>{observedHosts.length ? observedHosts.map((host) => <tr key={host.ip}><td className="sentinel-mono">{host.ip}</td><td>{host.packets.toLocaleString()}</td><td><span className="sentinel-proto-chip">Observed only</span></td></tr>) : <tr><td className="sentinel-table-empty" colSpan={3}>No source addresses observed yet</td></tr>}</tbody></table>}</div><footer className="sentinel-table-foot">{tab === "traffic" ? `Showing ${recentPackets.length} of the latest ${stats?.recent_packets.length ?? 0} packets` : `Showing ${observedHosts.length} top observed sources`} • No endpoint agent or device identity verification</footer></section>
          <div className="sentinel-footer">AEGIS / IDS · Local development dashboard · Built for network intrusion detection, not endpoint management</div>
        </div>
      </main>
    </div>
  );
}
