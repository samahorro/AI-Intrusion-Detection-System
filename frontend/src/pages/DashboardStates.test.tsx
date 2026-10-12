import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import Dashboard from "./Dashboard";

const mocks = vi.hoisted(() => ({
  getStats: vi.fn(),
  getInterfaces: vi.fn(),
  getStatus: vi.fn(),
  start: vi.fn(),
  stop: vi.fn(),
}));

vi.mock("../services/captureService", () => ({
  captureService: {
    getStats: mocks.getStats,
    getInterfaces: mocks.getInterfaces,
    getStatus: mocks.getStatus,
    start: mocks.start,
    stop: mocks.stop,
  },
}));

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

beforeEach(() => {
  mocks.getInterfaces.mockResolvedValue({
    interfaces: [
      {
        name: "Wi-Fi",
        description: "Wi-Fi",
      },
    ],
  });

  mocks.getStatus.mockResolvedValue({
    running: false,
    interface: null,
  });

  mocks.start.mockResolvedValue(undefined);
  mocks.stop.mockResolvedValue(undefined);
});

describe("Dashboard states", () => {
  it("renders backend error state when statistics fail to load", async () => {
    mocks.getStats.mockRejectedValue(new Error("Connection failed"));

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText("Backend unreachable")).toBeInTheDocument();
    });

    expect(
      screen.getByRole("alert", {
        name: "",
      }),
    ).toHaveTextContent("Backend error: Connection failed");
  });

  it("renders empty-state messages when no packets have been captured", async () => {
    mocks.getStats.mockResolvedValue({
      running: false,
      interface: null,
      packet_count: 0,
      total_bytes: 0,
      observed_source_ips: 0,
      protocols: {},
      last_packet_at: null,
      last_error: null,
      top_source_ips: [],
      recent_packets: [],
    });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText("Monitoring is stopped")).toBeInTheDocument();
    });

    expect(
      screen.getByText("No packets captured yet."),
    ).toBeInTheDocument();

    expect(
      screen.getByText("No source IPs observed yet."),
    ).toBeInTheDocument();

    expect(
      screen.getByText("Start capture to view packet metadata."),
    ).toBeInTheDocument();

    expect(screen.getByText("No packets yet")).toBeInTheDocument();
  });

  it("renders capture error feedback when the capture service reports an error", async () => {
    mocks.getStats.mockResolvedValue({
      running: false,
      interface: "Wi-Fi",
      packet_count: 0,
      total_bytes: 0,
      observed_source_ips: 0,
      protocols: {},
      last_packet_at: null,
      last_error: "TShark exited unexpectedly",
      top_source_ips: [],
      recent_packets: [],
    });

    render(<Dashboard />);

    await waitFor(() => {
      expect(
        screen.getByText("Capture error: TShark exited unexpectedly"),
      ).toBeInTheDocument();
    });
  });
});