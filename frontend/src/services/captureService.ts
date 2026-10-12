const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export type CaptureInterface = {
  number: number;
  name: string;
  description: string | null;
};

export type CaptureStatus = {
  running: boolean;
  interface: string | null;
};

async function apiRequest<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    credentials: "include",
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(error?.detail ?? `Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export type LivePacket = {
  timestamp: string;
  source_ip: string;
  destination_ip: string;
  protocol: string;
  length: number;
  source_port: string | null;
  destination_port: string | null;
};

export type SourceIPStats = {
  ip: string;
  packets: number;
};

export type CaptureStats = {
  running: boolean;
  interface: string | null;
  packet_count: number;
  total_bytes: number;
  observed_source_ips: number;
  protocols: Record<string, number>;
  top_source_ips: SourceIPStats[];
  recent_packets: LivePacket[];
  last_packet_at: string | null;
  last_error: string | null;
};

export const captureService = {
  async getInterfaces() {
    return apiRequest<{ interfaces: CaptureInterface[] }>(
      "/capture/interfaces",
    );
  },

  async getStatus() {
    return apiRequest<CaptureStatus>("/capture/status");
  },

  async getStats() {
    return apiRequest<CaptureStats>("/capture/stats");
  },

  async start(interfaceName: string) {
    return apiRequest("/capture/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ interface: interfaceName }),
    });
  },

  async stop() {
    return apiRequest("/capture/stop", {
      method: "POST",
    });
  },
};
