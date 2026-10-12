import { cleanup, render, screen } from "@testing-library/react";

import { afterEach, describe, expect, it, vi } from "vitest";

import Dashboard from "./Dashboard";

// Mock the network capture API so tests
// do not require a running FastAPI backend.
vi.mock("../services/captureService", () => ({
  captureService: {
    getStats: vi.fn().mockResolvedValue({
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
    }),
    getInterfaces: vi.fn().mockResolvedValue({
      interfaces: [],
    }),
    getStatus: vi.fn(),
    start: vi.fn(),
    stop: vi.fn(),
  },
}));

afterEach(() => {
  cleanup();
});

describe("Dashboard", () => {
  it("renders the dashboard heading", () => {
    render(<Dashboard />);

    expect(
      screen.getByRole("heading", {
        name: /ai-ids dashboard/i,
      }),
    ).toBeInTheDocument();
  });

  it("renders live network monitoring information", () => {
    render(<Dashboard />);

    expect(
      screen.getByRole("heading", {
        name: /monitoring status/i,
      }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("heading", {
        name: /network scan/i,
      }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("heading", {
        name: /^packets captured$/i,
      }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("heading", {
        name: /^data captured$/i,
      }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("heading", {
        name: /^observed source ips$/i,
      }),
    ).toBeInTheDocument();
  });

  it("renders network activity and detection status", () => {
    render(<Dashboard />);

    expect(
      screen.getByRole("heading", {
        name: /protocol distribution/i,
      }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("heading", {
        name: /top observed source ips/i,
      }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("heading", {
        name: /recent captured packets/i,
      }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("heading", {
        name: /ai threat detection/i,
      }),
    ).toBeInTheDocument();

    expect(
      screen.getByText(/not connected to live traffic yet/i),
    ).toBeInTheDocument();
  });
});
