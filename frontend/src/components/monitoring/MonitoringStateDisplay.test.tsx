import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import MonitoringStateDisplay from "./MonitoringStateDisplay";

afterEach(() => {
  cleanup();
});

describe("MonitoringStateDisplay", () => {
  it("renders the idle state", () => {
    render(<MonitoringStateDisplay state="idle" />);

    expect(screen.getByText("IDLE")).toBeInTheDocument();
    expect(screen.getByText("Monitoring is idle")).toBeInTheDocument();
  });

  it("renders the loading state", () => {
    render(<MonitoringStateDisplay state="loading" />);

    expect(screen.getByText("LOADING")).toBeInTheDocument();
    expect(
      screen.getByText("Loading monitoring data...")
    ).toBeInTheDocument();
  });

  it("renders the scanning state", () => {
    render(<MonitoringStateDisplay state="scanning" />);

    expect(screen.getByText("SCANNING")).toBeInTheDocument();
    expect(
      screen.getByText("Network scan in progress")
    ).toBeInTheDocument();
  });

  it("renders the monitoring state", () => {
    render(<MonitoringStateDisplay state="monitoring" />);

    expect(screen.getByText("MONITORING")).toBeInTheDocument();
    expect(
      screen.getByText("Monitoring is active")
    ).toBeInTheDocument();
  });

  it("renders the error state", () => {
    render(<MonitoringStateDisplay state="error" />);

    expect(screen.getByText("ERROR")).toBeInTheDocument();
    expect(
      screen.getByText("Monitoring encountered an error")
    ).toBeInTheDocument();
  });
});