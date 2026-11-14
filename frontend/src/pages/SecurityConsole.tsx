import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { Link } from "react-router-dom";
import { ProfileMenu } from "../components/ProfileMenu";

import {
  captureService,
  type CaptureInterface,
  type CaptureStats,
  type ExperimentalPredictionsResponse,
} from "../services/captureService";

import "./SecurityConsole.css";
import "../AEGISTheme.css";

type ConsoleTab = "traffic" | "hosts" | "ai";

type BlockedIpRecord = {
  id: number;
  ip_address: string;
  block_type: string;
  reason: string | null;
  status: string;
  created_by_user_id: number | null;
  created_at: string | null;
  expires_at: string | null;
};

type BlockedIpListResponse = {
  items: BlockedIpRecord[];
  total: number;
  simulation_only: boolean;
};

const API_BASE_URL = (
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_API_BASE_URL ||
  "http://localhost:8000"
).replace(/\/$/, "");

const bytesLabel = (value: number) =>
  value < 1024
    ? `${value} B`
    : value < 1048576
      ? `${(value / 1024).toFixed(1)} KB`
      : `${(value / 1048576).toFixed(2)} MB`;

const timeLabel = (value: string | null | undefined) =>
  value ? new Date(value).toLocaleTimeString() : "—";

const scoreLabel = (value: number) =>
  `${(value * 100).toFixed(2)}%`;

export default function SecurityConsole() {
  const [stats, setStats] = useState<CaptureStats | null>(null);

  const [interfaces, setInterfaces] =
    useState<CaptureInterface[]>([]);

  const [selectedInterface, setSelectedInterface] =
    useState("");

  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [refreshAt, setRefreshAt] = useState("");
  const [filter, setFilter] = useState("");

  const [tab, setTab] = useState<ConsoleTab>("traffic");

  const activitySectionRef =
    useRef<HTMLElement | null>(null);

  // ---------------------------------------------------------
  // Simulated IP management state
  // ---------------------------------------------------------

  const [blockedIps, setBlockedIps] =
    useState<BlockedIpRecord[]>([]);

  const [selectedBlockIp, setSelectedBlockIp] =
    useState<string | null>(null);

  const [blockReason, setBlockReason] = useState("");

  const [ipActionBusy, setIpActionBusy] =
    useState(false);

  const [ipActionError, setIpActionError] =
    useState("");

  const [ipActionSuccess, setIpActionSuccess] =
    useState("");

  // ---------------------------------------------------------
  // Experimental AI detection state
  // ---------------------------------------------------------

  const [aiResults, setAiResults] =
    useState<ExperimentalPredictionsResponse | null>(
      null,
    );

  const [aiError, setAiError] = useState("");

  // ---------------------------------------------------------
  // Capture statistics polling
  // ---------------------------------------------------------

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
        if (active) {
          setError(
            e instanceof Error
              ? e.message
              : "Failed to fetch live statistics",
          );
        }
      } finally {
        pending = false;
      }
    }

    async function initialize() {
      try {
        const result =
          await captureService.getInterfaces();

        if (!active) return;

        setInterfaces(result.interfaces);

        const wifi = result.interfaces.find(
          (item) =>
            item.description?.includes("Wi-Fi") ||
            item.name === "Wi-Fi",
        );

        setSelectedInterface(
          wifi?.name ??
            result.interfaces[0]?.name ??
            "",
        );
      } catch (e) {
        if (active) {
          setError(
            e instanceof Error
              ? e.message
              : "Cannot list interfaces",
          );
        }
      }
    }

    void initialize();
    void refresh();

    const timer = window.setInterval(
      () => void refresh(),
      2000,
    );

    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, []);

  // ---------------------------------------------------------
  // Experimental AI predictions polling
  // ---------------------------------------------------------

  useEffect(() => {
    let active = true;
    let pending = false;

    async function refreshAI() {
      if (pending) return;

      pending = true;

      try {
        const results =
          await captureService.getExperimentalPredictions();

        if (active) {
          setAiResults(results);
          setAiError("");
        }
      } catch (e) {
        if (active) {
          setAiError(
            e instanceof Error
              ? e.message
              : "Unable to fetch AI predictions",
          );
        }
      } finally {
        pending = false;
      }
    }

    void refreshAI();

    const timer = window.setInterval(
      () => void refreshAI(),
      5000,
    );

    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, []);

  // ---------------------------------------------------------
  // Simulated IP management
  // ---------------------------------------------------------

  async function loadBlockedIps() {
    try {
      const response = await fetch(
        `${API_BASE_URL}/blocked-ips`,
        {
          method: "GET",
          credentials: "include",
        },
      );

      if (!response.ok) {
        throw new Error(
          `Unable to load blocked IPs (${response.status})`,
        );
      }

      const data =
        (await response.json()) as BlockedIpListResponse;

      setBlockedIps(data.items);
      setIpActionError("");
    } catch (e) {
      setIpActionError(
        e instanceof Error
          ? e.message
          : "Unable to load blocked IP addresses",
      );
    }
  }

  useEffect(() => {
    void loadBlockedIps();
  }, []);

  function isIpBlocked(ip: string) {
    return blockedIps.some(
      (record) =>
        record.ip_address === ip &&
        record.status.toLowerCase() !== "unblocked",
    );
  }

  function openObservedHosts() {
    setTab("hosts");

    window.setTimeout(() => {
      activitySectionRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }, 0);
  }

  async function handleConfirmBlock() {
    if (!selectedBlockIp || ipActionBusy) {
      return;
    }

    setIpActionBusy(true);
    setIpActionError("");
    setIpActionSuccess("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/blocked-ips`,
        {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            ip_address: selectedBlockIp,
            reason: blockReason.trim() || null,
          }),
        },
      );

      if (!response.ok) {
        let detail = "";

        try {
          const body = await response.json();

          detail =
            typeof body?.detail === "string"
              ? `: ${body.detail}`
              : "";
        } catch {
          // Ignore an unreadable error body.
        }

        throw new Error(
          `Unable to block IP (${response.status})${detail}`,
        );
      }

      const blockedIp = selectedBlockIp;

      setSelectedBlockIp(null);
      setBlockReason("");

      await loadBlockedIps();

      setIpActionSuccess(
        `${blockedIp} was added to the simulated blocked-IP list.`,
      );
    } catch (e) {
      setIpActionError(
        e instanceof Error
          ? e.message
          : "Unable to block IP",
      );
    } finally {
      setIpActionBusy(false);
    }
  }

  async function handleUnblockIp(ip: string) {
    if (ipActionBusy) return;

    setIpActionBusy(true);
    setIpActionError("");
    setIpActionSuccess("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/blocked-ips/${encodeURIComponent(
          ip,
        )}`,
        {
          method: "DELETE",
          credentials: "include",
        },
      );

      if (!response.ok) {
        let detail = "";

        try {
          const body = await response.json();

          detail =
            typeof body?.detail === "string"
              ? `: ${body.detail}`
              : "";
        } catch {
          // Ignore an unreadable error body.
        }

        throw new Error(
          `Unable to unblock IP (${response.status})${detail}`,
        );
      }

      await loadBlockedIps();

      setIpActionSuccess(
        `${ip} was successfully unblocked.`,
      );
    } catch (e) {
      setIpActionError(
        e instanceof Error
          ? e.message
          : "Unable to unblock IP",
      );
    } finally {
      setIpActionBusy(false);
    }
  }

  // ---------------------------------------------------------
  // Start / stop live capture
  // ---------------------------------------------------------

  async function toggleCapture() {
    if (busy) return;

    setBusy(true);
    setError("");

    try {
      if (stats?.running) {
        await captureService.stop();
      } else {
        if (!selectedInterface) {
          throw new Error(
            "Select a network interface first",
          );
        }

        await captureService.start(selectedInterface);

        // Clear results from the previous capture session.
        setAiResults(null);
      }
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Capture command failed",
      );
    } finally {
      try {
        setStats(await captureService.getStats());
      } catch {
        setError("Unable to verify capture status");
      }

      setBusy(false);
    }
  }

  // ---------------------------------------------------------
  // Derived network statistics
  // ---------------------------------------------------------

  const packets = stats?.packet_count ?? 0;

  const protocols = useMemo(
    () =>
      Object.entries(stats?.protocols ?? {}).sort(
        (a, b) => b[1] - a[1],
      ),
    [stats],
  );

  const query = filter.trim().toLowerCase();

  const recentPackets = (stats?.recent_packets ?? []).filter(
    (packet) =>
      `${packet.source_ip} ${packet.destination_ip} ` +
      `${packet.protocol} ${packet.source_port ?? ""} ` +
      `${packet.destination_port ?? ""}`
        .toLowerCase()
        .includes(query),
  );

  const observedHosts = (stats?.top_source_ips ?? []).filter(
    (host) =>
      host.ip.toLowerCase().includes(query),
  );

  // ---------------------------------------------------------
  // Derived AI detection statistics
  // ---------------------------------------------------------

  const predictions = aiResults?.predictions ?? [];

  const analyzedFlows = predictions.length;

  const benignCount = predictions.filter(
    (flow) =>
      flow.ai_detection.prediction === "BENIGN",
  ).length;

  const attackCount = predictions.filter(
    (flow) =>
      flow.ai_detection.prediction === "ATTACK",
  ).length;

  const highestScore = predictions.length
    ? Math.max(
        ...predictions.map(
          (flow) =>
            flow.ai_detection.attack_probability,
        ),
      )
    : null;

  const filteredPredictions = predictions
    .filter((flow) =>
      (
        `${flow.source_ip} ${flow.destination_ip} ` +
        `${flow.protocol} ${flow.source_port ?? ""} ` +
        `${flow.destination_port ?? ""} ` +
        `${flow.ai_detection.prediction}`
      )
        .toLowerCase()
        .includes(query),
    )
    .sort(
      (a, b) =>
        b.ai_detection.attack_probability -
        a.ai_detection.attack_probability,
    );

  // ---------------------------------------------------------
  // Component
  // ---------------------------------------------------------

  return (
    <div className="sentinel-console">
      {/* Sidebar */}
      <aside className="sentinel-sidebar">
        <div className="sentinel-brand">
          <span className="sentinel-brand-logo">
            ◈
          </span>

          <span>
            AEGIS
            <span className="sentinel-brand-accent">
              {" "}
              / IDS
            </span>
            <small>
              NETWORK DEFENSE CONSOLE
            </small>
          </span>
        </div>

        <div className="sentinel-nav-label">
          WORKSPACE
        </div>

        <div className="sentinel-nav-selected">
          ▦ <span>Security overview</span>
        </div>

        <button
          className="sentinel-nav-link"
          onClick={() => setTab("traffic")}
          aria-current={
            tab === "traffic"
              ? "page"
              : undefined
          }
        >
          ≋ <span>Network traffic</span>
        </button>

        <button
          className="sentinel-nav-link"
          onClick={openObservedHosts}
          aria-current={
            tab === "hosts"
              ? "page"
              : undefined
          }
        >
          ▧ <span>Observed hosts</span>
        </button>

        <div className="sentinel-nav-label sentinel-section-space">
          DETECTION
        </div>

        <button
          className="sentinel-nav-link"
          onClick={() => setTab("ai")}
          aria-current={
            tab === "ai"
              ? "page"
              : undefined
          }
        >
          ◇{" "}
          <span>
            AI detections (Experimental)
          </span>
        </button>

        <div className="sentinel-nav-muted">
          ▤{" "}
          <span>
            Incident alerts <i>Coming soon</i>
          </span>
        </div>

        <div className="sentinel-nav-foot">
          <Link to="/dashboard">
            ← Original dashboard
          </Link>

          <span>
            Live telemetry • Local session
          </span>
        </div>
      </aside>

      {/* Main */}
      <main className="sentinel-main">
        <header className="sentinel-topbar">
          <div>
            <span className="sentinel-breadcrumb">
              SECURITY OPERATIONS
            </span>

            <span className="sentinel-slash">
              {" "}
              /{" "}
            </span>

            Overview
          </div>

          <div className="sentinel-topright">
            <span className="sentinel-live-dot" />

            LIVE API

            <span className="sentinel-separator">
              |
            </span>

            {refreshAt || "Connecting..."}

            <ProfileMenu />
          </div>
        </header>

        <div className="sentinel-content">
          {/* Heading */}
          <div className="sentinel-heading">
            <div>
              <div className="sentinel-eyebrow">
                NETWORK VISIBILITY
              </div>

              <h1>Security Overview</h1>

              <p>
                Real-time packet telemetry and experimental
                AI intrusion detection
              </p>
            </div>

            <div
              className={`sentinel-state ${
                stats?.running ? "is-running" : ""
              }`}
            >
              <span className="sentinel-state-dot" />

              {error
                ? "Backend error"
                : stats?.running
                  ? "Capture active"
                  : "Capture stopped"}
            </div>
          </div>

          {/* Errors */}
          {error && (
            <div
              className="sentinel-error"
              role="alert"
            >
              Connection error: {error}
            </div>
          )}

          {stats?.last_error && (
            <div
              className="sentinel-error"
              role="alert"
            >
              TShark: {stats.last_error}
            </div>
          )}

          {aiError && (
            <div
              className="sentinel-error"
              role="alert"
            >
              AI detection error: {aiError}
            </div>
          )}

          {/* Capture controls */}
          <section
            className="sentinel-capture-bar"
            aria-label="Capture controls"
          >
            <div>
              <div className="sentinel-control-label">
                MONITORING INTERFACE
              </div>

              <select
                aria-label="Capture interface"
                disabled={
                  busy || Boolean(stats?.running)
                }
                value={
                  stats?.running
                    ? stats.interface ?? selectedInterface
                    : selectedInterface
                }
                onChange={(e) =>
                  setSelectedInterface(e.target.value)
                }
              >
                <option value="">
                  Select interface
                </option>

                {interfaces.map((item) => (
                  <option
                    key={item.name}
                    value={item.name}
                  >
                    {item.description || item.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="sentinel-capture-actions">
              <span className="sentinel-capture-hint">
                {stats?.running
                  ? "Packets are being captured"
                  : "Ready to monitor"}
              </span>

              <button
                onClick={() => void toggleCapture()}
                disabled={
                  busy ||
                  (!stats?.running &&
                    !selectedInterface)
                }
                className={`sentinel-capture-button ${
                  stats?.running ? "is-stop" : ""
                }`}
              >
                {busy
                  ? "Working..."
                  : stats?.running
                    ? "■ Stop capture"
                    : "▶ Start capture"}
              </button>
            </div>
          </section>

          {/* Main packet metrics */}
          <section
            className="sentinel-metrics"
            aria-label="Live network metrics"
          >
            <div className="sentinel-metric">
              <span>TOTAL PACKETS</span>
              <strong>
                {packets.toLocaleString()}
              </strong>
              <small>
                Current capture session
              </small>
              <b>↗</b>
            </div>

            <div className="sentinel-metric">
              <span>DATA OBSERVED</span>
              <strong>
                {bytesLabel(
                  stats?.total_bytes ?? 0,
                )}
              </strong>
              <small>
                Captured frame bytes
              </small>
              <b>◫</b>
            </div>

            <div className="sentinel-metric">
              <span>
                UNIQUE SOURCE IPS
              </span>
              <strong>
                {(
                  stats?.observed_source_ips ?? 0
                ).toLocaleString()}
              </strong>
              <small>
                Not necessarily devices
              </small>
              <b>⌘</b>
            </div>

            <div className="sentinel-metric">
              <span>LAST PACKET</span>
              <strong className="sentinel-metric-time">
                {timeLabel(
                  stats?.last_packet_at,
                )}
              </strong>
              <small>Local time</small>
              <b>◷</b>
            </div>
          </section>

          {/* Protocol + Detection overview */}
          <div className="sentinel-panels">
            <section className="sentinel-panel">
              <div className="sentinel-panel-head">
                <div>
                  <h2>
                    Protocol distribution
                  </h2>
                  <p>
                    Traffic by transport
                    protocol
                  </p>
                </div>

                <span className="sentinel-panel-tag">
                  LIVE
                </span>
              </div>

              {packets ? (
                <div className="sentinel-protocols">
                  {protocols.map(
                    ([name, count], index) => (
                      <div
                        className="sentinel-protocol"
                        key={name}
                      >
                        <div>
                          <span
                            className={`sentinel-protocol-square square-${
                              index % 4
                            }`}
                          />

                          <strong>
                            {name}
                          </strong>

                          <span>
                            {count.toLocaleString()} packets
                          </span>

                          <em>
                            {(
                              (100 * count) /
                              packets
                            ).toFixed(1)}
                            %
                          </em>
                        </div>

                        <div className="sentinel-protocol-track">
                          <div
                            className={`sentinel-protocol-fill fill-${
                              index % 4
                            }`}
                            style={{
                              width: `${
                                (100 * count) /
                                packets
                              }%`,
                            }}
                          />
                        </div>
                      </div>
                    ),
                  )}
                </div>
              ) : (
                <p className="sentinel-empty">
                  Start capture to see
                  protocol activity.
                </p>
              )}
            </section>

            {/* AI Detection Engine */}
            <section className="sentinel-panel">
              <div className="sentinel-panel-head">
                <div>
                  <h2>
                    Detection engine
                  </h2>
                  <p>
                    AEGIS Random Forest v1
                  </p>
                </div>

                <span className="sentinel-panel-tag muted">
                  EXPERIMENTAL
                </span>
              </div>

              <div style={{ padding: "16px" }}>
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns:
                      "repeat(2, minmax(0, 1fr))",
                    gap: "12px",
                  }}
                >
                  <div>
                    <small>
                      FLOWS ANALYZED
                    </small>
                    <h2>
                      {analyzedFlows}
                    </h2>
                  </div>

                  <div>
                    <small>
                      PREDICTED ATTACKS
                    </small>

                    <h2
                      style={{
                        color: "#ef4444",
                      }}
                    >
                      {attackCount}
                    </h2>
                  </div>

                  <div>
                    <small>
                      PREDICTED BENIGN
                    </small>

                    <h2
                      style={{
                        color: "#22c55e",
                      }}
                    >
                      {benignCount}
                    </h2>
                  </div>

                  <div>
                    <small>
                      HIGHEST ATTACK SCORE
                    </small>

                    <h2>
                      {highestScore === null
                        ? "N/A"
                        : scoreLabel(
                            highestScore,
                          )}
                    </h2>
                  </div>
                </div>

                <p
                  style={{
                    marginTop: 16,
                    fontSize: 12,
                  }}
                >
                  Recent completed-flow predictions only.
                  Model scores are not verified security
                  threats.
                </p>

                <p
                  style={{
                    fontSize: 12,
                  }}
                >
                  Automated alerts: Disabled
                </p>

                <button
                  className="sentinel-nav-link"
                  onClick={() => setTab("ai")}
                >
                  View AI predictions →
                </button>
              </div>
            </section>
          </div>

          {/* Activity / AI Detection Tables */}
          <section
            ref={activitySectionRef}
            className="sentinel-panel sentinel-activity"
          >
            <div className="sentinel-panel-head">
              <div>
                <h2>
                  {tab === "ai"
                    ? "Experimental AI detections"
                    : tab === "hosts"
                      ? "Observed hosts"
                      : "Network activity"}
                </h2>

                <p>
                  {tab === "ai"
                    ? "Completed network flows classified by Random Forest"
                    : tab === "hosts"
                      ? "Observed source addresses from captured network activity"
                      : "Latest captured packets and observed source addresses"}
                </p>
              </div>

              <span className="sentinel-panel-tag">
                {tab === "ai"
                  ? "AUTO-REFRESH • 5S"
                  : "AUTO-REFRESH • 2S"}
              </span>
            </div>

            {/* Tabs and search */}
            <div className="sentinel-table-tools">
              <div className="sentinel-tabs">
                <button
                  className={
                    tab === "traffic"
                      ? "active"
                      : ""
                  }
                  onClick={() =>
                    setTab("traffic")
                  }
                >
                  Packet activity
                </button>

                <button
                  className={
                    tab === "hosts"
                      ? "active"
                      : ""
                  }
                  onClick={() =>
                    setTab("hosts")
                  }
                >
                  Observed sources
                </button>

                <button
                  className={
                    tab === "ai"
                      ? "active"
                      : ""
                  }
                  onClick={() =>
                    setTab("ai")
                  }
                >
                  AI detections ({attackCount})
                </button>
              </div>

              <input
                aria-label="Filter traffic or addresses"
                placeholder="Filter IP, protocol, port or prediction..."
                value={filter}
                onChange={(e) =>
                  setFilter(e.target.value)
                }
              />
            </div>

            {/* IP management feedback */}
            {tab === "hosts" &&
              ipActionError && (
                <div
                  className="sentinel-error"
                  role="alert"
                >
                  IP management:{" "}
                  {ipActionError}
                </div>
              )}

            {tab === "hosts" &&
              ipActionSuccess && (
                <div role="status">
                  {ipActionSuccess}
                </div>
              )}

            {/* Block confirmation form */}
            {tab === "hosts" &&
              selectedBlockIp && (
                <div
                  className="sentinel-panel"
                  style={{
                    margin: "16px",
                    padding: "16px",
                  }}
                >
                  <h3>
                    Confirm simulated IP block
                  </h3>

                  <p>
                    Add{" "}
                    <strong>
                      {selectedBlockIp}
                    </strong>{" "}
                    to the simulated blocked-IP
                    list?
                  </p>

                  <label
                    htmlFor="block-reason"
                    className="sentinel-control-label"
                  >
                    REASON
                  </label>

                  <input
                    id="block-reason"
                    type="text"
                    value={blockReason}
                    maxLength={255}
                    placeholder="Reason for blocking this IP (optional)"
                    disabled={ipActionBusy}
                    onChange={(e) =>
                      setBlockReason(
                        e.target.value,
                      )
                    }
                  />

                  <div
                    style={{
                      display: "flex",
                      gap: "12px",
                      marginTop: "12px",
                    }}
                  >
                    <button
                      type="button"
                      className="sentinel-capture-button is-stop"
                      disabled={ipActionBusy}
                      onClick={() =>
                        void handleConfirmBlock()
                      }
                    >
                      {ipActionBusy
                        ? "Blocking..."
                        : "Confirm"}
                    </button>

                    <button
                      type="button"
                      className="sentinel-nav-link"
                      disabled={ipActionBusy}
                      onClick={() => {
                        setSelectedBlockIp(null);
                        setBlockReason("");
                        setIpActionError("");
                      }}
                    >
                      Cancel
                    </button>
                  </div>

                  <p
                    style={{
                      marginTop: "12px",
                      fontSize: "12px",
                    }}
                  >
                    Simulation only. This action
                    does not modify the
                    operating-system firewall.
                  </p>
                </div>
              )}

            <div className="sentinel-table-wrap">
              {/* Packet activity */}
              {tab === "traffic" && (
                <table>
                  <thead>
                    <tr>
                      <th>TIME</th>
                      <th>SOURCE IP</th>
                      <th>
                        DESTINATION IP
                      </th>
                      <th>PROTOCOL</th>
                      <th>BYTES</th>
                    </tr>
                  </thead>

                  <tbody>
                    {recentPackets.length ? (
                      recentPackets.map(
                        (
                          packet,
                          index,
                        ) => (
                          <tr
                            key={`${packet.timestamp}-${index}`}
                          >
                            <td>
                              {timeLabel(
                                packet.timestamp,
                              )}
                            </td>

                            <td className="sentinel-mono">
                              {packet.source_ip ||
                                "—"}
                            </td>

                            <td className="sentinel-mono">
                              {packet.destination_ip ||
                                "—"}
                            </td>

                            <td>
                              <span className="sentinel-proto-chip">
                                {
                                  packet.protocol
                                }
                              </span>
                            </td>

                            <td>
                              {packet.length.toLocaleString()}
                            </td>
                          </tr>
                        ),
                      )
                    ) : (
                      <tr>
                        <td
                          className="sentinel-table-empty"
                          colSpan={5}
                        >
                          No matching packets
                          captured yet
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              )}

              {/* Observed sources */}
              {tab === "hosts" && (
                <table>
                  <thead>
                    <tr>
                      <th>SOURCE IP</th>
                      <th>
                        PACKETS OBSERVED
                      </th>
                      <th>VISIBILITY</th>
                      <th>ACTION</th>
                    </tr>
                  </thead>

                  <tbody>
                    {observedHosts.length ? (
                      observedHosts.map(
                        (host) => {
                          const blocked =
                            isIpBlocked(
                              host.ip,
                            );

                          return (
                            <tr key={host.ip}>
                              <td className="sentinel-mono">
                                {host.ip}
                              </td>

                              <td>
                                {host.packets.toLocaleString()}
                              </td>

                              <td>
                                <span className="sentinel-proto-chip">
                                  {blocked
                                    ? "Simulated blocked"
                                    : "Observed only"}
                                </span>
                              </td>

                              <td>
                                {blocked ? (
                                  <button
                                    type="button"
                                    className="sentinel-capture-button"
                                    disabled={
                                      ipActionBusy
                                    }
                                    onClick={() =>
                                      void handleUnblockIp(
                                        host.ip,
                                      )
                                    }
                                  >
                                    Unblock IP
                                  </button>
                                ) : (
                                  <button
                                    type="button"
                                    className="sentinel-capture-button is-stop"
                                    disabled={
                                      ipActionBusy
                                    }
                                    onClick={() => {
                                      setSelectedBlockIp(
                                        host.ip,
                                      );
                                      setBlockReason(
                                        "",
                                      );
                                      setIpActionError(
                                        "",
                                      );
                                      setIpActionSuccess(
                                        "",
                                      );
                                    }}
                                  >
                                    Block IP
                                  </button>
                                )}
                              </td>
                            </tr>
                          );
                        },
                      )
                    ) : (
                      <tr>
                        <td
                          className="sentinel-table-empty"
                          colSpan={4}
                        >
                          No source addresses
                          observed yet
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              )}

              {/* Experimental AI predictions */}
              {tab === "ai" && (
                <table>
                  <thead>
                    <tr>
                      <th>SOURCE IP</th>
                      <th>
                        DESTINATION IP
                      </th>
                      <th>PROTOCOL</th>
                      <th>PACKETS</th>
                      <th>PREDICTION</th>
                      <th>
                        ATTACK SCORE
                      </th>
                      <th>COMPLETION</th>
                    </tr>
                  </thead>

                  <tbody>
                    {filteredPredictions.length ? (
                      filteredPredictions.map(
                        (
                          flow,
                          index,
                        ) => {
                          const isAttack =
                            flow.ai_detection
                              .prediction ===
                            "ATTACK";

                          return (
                            <tr key={index}>
                              <td className="sentinel-mono">
                                {
                                  flow.source_ip
                                }
                                <small>
                                  :
                                  {flow.source_port ??
                                    "-"}
                                </small>
                              </td>

                              <td className="sentinel-mono">
                                {
                                  flow.destination_ip
                                }
                                <small>
                                  :
                                  {flow.destination_port ??
                                    "-"}
                                </small>
                              </td>

                              <td>
                                <span className="sentinel-proto-chip">
                                  {
                                    flow.protocol
                                  }
                                </span>
                              </td>

                              <td>
                                {
                                  flow.packet_count
                                }
                              </td>

                              <td>
                                <strong
                                  style={{
                                    color:
                                      isAttack
                                        ? "#ef4444"
                                        : "#22c55e",
                                  }}
                                >
                                  {
                                    flow
                                      .ai_detection
                                      .prediction
                                  }
                                </strong>
                              </td>

                              <td>
                                {scoreLabel(
                                  flow
                                    .ai_detection
                                    .attack_probability,
                                )}
                              </td>

                              <td>
                                {flow.completion_reason ??
                                  "-"}
                              </td>
                            </tr>
                          );
                        },
                      )
                    ) : (
                      <tr>
                        <td
                          className="sentinel-table-empty"
                          colSpan={7}
                        >
                          No completed flows match the
                          current filter. Start or stop
                          capture to generate predictions.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              )}
            </div>

            <footer className="sentinel-table-foot">
              {tab === "traffic"
                ? `Showing ${recentPackets.length} of the latest ${
                    stats?.recent_packets.length ?? 0
                  } packets`
                : tab === "hosts"
                  ? `Showing ${observedHosts.length} top observed sources`
                  : `Showing ${filteredPredictions.length} of ${
                      aiResults?.prediction_count ?? 0
                    } recent experimental flow predictions`}

              {" • "}

              {tab === "ai"
                ? "Not confirmed security incidents"
                : tab === "hosts"
                  ? "Block actions are simulation only"
                  : "No endpoint agent or device identity verification"}
            </footer>
          </section>

          {/* Footer */}
          <div className="sentinel-footer">
            AEGIS / IDS · Local development dashboard ·
            Experimental network intrusion detection
          </div>
        </div>
      </main>
    </div>
  );
}