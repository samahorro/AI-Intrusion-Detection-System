import { useState } from "react";

export default function ScanNetworkControl() {
  const [isScanning, setIsScanning] = useState(false);

  const handleScan = () => {
    setIsScanning(true);

    setTimeout(() => {
      setIsScanning(false);
    }, 2000);
  };

  return (
    <div className="scan-network-control">
      <button
        type="button"
        onClick={handleScan}
        disabled={isScanning}
      >
        {isScanning ? "Scanning..." : "Scan Network"}
      </button>

      <span>
        {isScanning
          ? "Network scan in progress"
          : "Ready to scan"}
      </span>
    </div>
  );
}