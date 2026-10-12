import { useEffect, useState } from "react";
import {
  captureService,
  type CaptureInterface,
} from "../../services/captureService";

export default function ScanNetworkControl() {
  const [interfaces, setInterfaces] = useState<CaptureInterface[]>([]);
  const [selectedInterface, setSelectedInterface] = useState("");
  const [isScanning, setIsScanning] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    async function initialize() {
      try {
        const [interfaceData, status] = await Promise.all([
          captureService.getInterfaces(),
          captureService.getStatus(),
        ]);
        if (!active) return;
        setInterfaces(interfaceData.interfaces);
        setIsScanning(status.running);
        const wifi = interfaceData.interfaces.find(
          (item: CaptureInterface) =>
            item.description?.includes("Wi-Fi") || item.name === "Wi-Fi",
        );
        setSelectedInterface(
          status.interface ??
            wifi?.name ??
            interfaceData.interfaces[0]?.name ??
            "",
        );
      } catch (err) {
        if (active)
          setError(err instanceof Error ? err.message : "Connection failed");
      } finally {
        if (active) setLoading(false);
      }
    }
    void initialize();
    return () => {
      active = false;
    };
  }, []);

  // Keep this control in sync if capture was started/stopped outside the page.
  useEffect(() => {
    const timer = window.setInterval(async () => {
      if (loading) return;
      try {
        const status = await captureService.getStatus();
        setIsScanning(status.running);
      } catch {
        /* Errors from manual actions remain visible. */
      }
    }, 3000);
    return () => window.clearInterval(timer);
  }, [loading]);

  async function handleScan() {
    if (loading) return;
    setLoading(true);
    setError("");
    try {
      if (isScanning) await captureService.stop();
      else await captureService.start(selectedInterface);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Capture failed");
    } finally {
      try {
        const status = await captureService.getStatus();
        setIsScanning(status.running);
      } catch {
        setError("Unable to verify capture status");
      }
      setLoading(false);
    }
  }

  return (
    <div className="scan-network-control">
      <label htmlFor="network-interface">Network Interface: </label>
      <select
        id="network-interface"
        value={selectedInterface}
        onChange={(e) => setSelectedInterface(e.target.value)}
        disabled={isScanning || loading}
      >
        {interfaces.map((item) => (
          <option key={item.name} value={item.name}>
            {item.description || item.name}
          </option>
        ))}
      </select>{" "}
      <button
        type="button"
        onClick={() => void handleScan()}
        disabled={loading || (!isScanning && !selectedInterface)}
      >
        {loading ? "Please wait..." : isScanning ? "Stop Scan" : "Scan Network"}
      </button>{" "}
      <span>
        {isScanning ? "TShark capture process running" : "Capture stopped"}
      </span>
      {error && (
        <p role="alert" style={{ color: "red" }}>
          {error}
        </p>
      )}
    </div>
  );
}
