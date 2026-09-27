import {
  cleanup,
  render,
  screen,
} from "@testing-library/react";

import {
  afterEach,
  describe,
  expect,
  it,
} from "vitest";

import Dashboard from "./Dashboard";

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

  it("renders monitored device information", () => {
    render(<Dashboard />);

    expect(
      screen.getByText(/monitored devices/i),
    ).toBeInTheDocument();

    expect(
      screen.getByText("desktop-01"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("192.168.1.10"),
    ).toBeInTheDocument();
  });

  it("renders recent alerts", () => {
    render(<Dashboard />);

    expect(
      screen.getByText(/recent alerts/i),
    ).toBeInTheDocument();

    expect(
      screen.getByText("Port Scan"),
    ).toBeInTheDocument();
  });
});