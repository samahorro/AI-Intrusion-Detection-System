import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import DeviceTable from "./DeviceTable";

afterEach(() => {
  cleanup();
});

describe("DeviceTable", () => {
  it("renders device information", () => {
    const devices = [
      {
        id: 1,
        ip: "192.168.1.10",
        hostname: "desktop-01",
        status: "online" as const,
      },
      {
        id: 2,
        ip: "192.168.1.15",
        hostname: "server-01",
        status: "offline" as const,
      },
    ];

    render(<DeviceTable devices={devices} />);

    expect(screen.getByText("desktop-01")).toBeInTheDocument();
    expect(screen.getByText("192.168.1.10")).toBeInTheDocument();
    expect(screen.getByText("ONLINE")).toBeInTheDocument();

    expect(screen.getByText("server-01")).toBeInTheDocument();
    expect(screen.getByText("192.168.1.15")).toBeInTheDocument();
    expect(screen.getByText("OFFLINE")).toBeInTheDocument();
  });

  it("renders the empty state when no devices are provided", () => {
    render(<DeviceTable devices={[]} />);

    expect(
      screen.getByText("No monitored devices found.")
    ).toBeInTheDocument();
  });
});