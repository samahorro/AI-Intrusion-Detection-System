import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import Alerts from "./Alerts";

afterEach(() => {
  cleanup();
});

describe("Alerts", () => {
  it("renders the alerts page heading", () => {
    render(<Alerts />);

    expect(
      screen.getByRole("heading", { name: /threat alerts/i }),
    ).toBeInTheDocument();
  });

  it("renders representative alert details", () => {
    render(<Alerts />);

    expect(screen.getByText("Port Scan")).toBeInTheDocument();
    expect(screen.getByText("192.168.1.21")).toBeInTheDocument();
    expect(screen.getByText("22")).toBeInTheDocument();
    expect(screen.getByText("94%")).toBeInTheDocument();
  });

  it("renders multiple alert types", () => {
    render(<Alerts />);

    expect(screen.getByText("Port Scan")).toBeInTheDocument();
    expect(screen.getByText("Suspicious Traffic")).toBeInTheDocument();
  });

  it("renders threat severity badges", () => {
    render(<Alerts />);

    expect(screen.getByText("HIGH")).toBeInTheDocument();
    expect(screen.getByText("MEDIUM")).toBeInTheDocument();
  });

  // Sprint 4 - SOC 2 CC7.3
  it("keeps security event information associated with the correct alert", () => {
    render(<Alerts />);

    const alertCards = screen.getAllByRole("article");
    expect(alertCards.length).toBeGreaterThan(1);

    const firstAlert = alertCards[0];

    expect(within(firstAlert).getByText("HIGH")).toBeInTheDocument();
    expect(within(firstAlert).getByText("Port Scan")).toBeInTheDocument();

    expect(firstAlert).toHaveTextContent("Source IP: 192.168.1.21");
    expect(firstAlert).toHaveTextContent("Port: 22");
    expect(firstAlert).toHaveTextContent("Detected:");
    expect(firstAlert).toHaveTextContent("AI Confidence: 94%");
  });

  it("presents multiple security events as separate alert records", () => {
    render(<Alerts />);

    const alertCards = screen.getAllByRole("article");

    expect(alertCards.length).toBeGreaterThanOrEqual(2);

    expect(alertCards[0]).toHaveTextContent("Port Scan");
    expect(alertCards[0]).toHaveTextContent("HIGH");

    expect(alertCards[1]).toHaveTextContent("Suspicious Traffic");
    expect(alertCards[1]).toHaveTextContent("MEDIUM");
  });
});

// Sprint 4 - SOC 2 CC7.3 edge-case validation
it("shows a safe empty state when there are no alerts", () => {
  render(<Alerts alerts={[]} />);

  expect(
    screen.getByText("No security alerts available."),
  ).toBeInTheDocument();
});

it("handles missing security event fields safely", () => {
  const incompleteAlert = [
    {
      id: 100,
      severity: "high" as const,
      attackType: "Port Scan",
      timestamp: "2026-10-31 12:00",
    },
  ];

  render(<Alerts alerts={incompleteAlert} />);

  const alertCard = screen.getByRole("article");

  expect(alertCard).toHaveTextContent("Port Scan");
  expect(alertCard).toHaveTextContent("Source IP: Unavailable");
  expect(alertCard).toHaveTextContent("Port: Unavailable");
  expect(alertCard).toHaveTextContent(
    "AI Confidence: Unavailable",
  );
});

it("handles missing attack type safely", () => {
  const incompleteAlert = [
    {
      id: 101,
      severity: "medium" as const,
      ip: "192.168.1.50",
      port: 443,
      timestamp: "2026-10-31 12:00",
      confidence: 0.81,
    },
  ];

  render(<Alerts alerts={incompleteAlert} />);

  expect(
    screen.getByText("Unknown Event"),
  ).toBeInTheDocument();
});

it("handles invalid confidence values safely", () => {
  const invalidAlert = [
    {
      id: 102,
      severity: "high" as const,
      ip: "192.168.1.21",
      port: 22,
      attackType: "Port Scan",
      timestamp: "2026-10-31 12:00",
      confidence: 1.5,
    },
  ];

  render(<Alerts alerts={invalidAlert} />);

  expect(
    screen.getByText("Unavailable"),
  ).toBeInTheDocument();

  expect(
    screen.queryByText("150%"),
  ).not.toBeInTheDocument();
});

it("handles missing severity safely", () => {
  const incompleteAlert = [
    {
      id: 103,
      ip: "192.168.1.45",
      port: 443,
      attackType: "Suspicious Traffic",
      timestamp: "2026-10-31 12:00",
      confidence: 0.81,
    },
  ];

  render(<Alerts alerts={incompleteAlert} />);

  expect(
    screen.getByText("Severity: Unavailable"),
  ).toBeInTheDocument();
});

// Sprint 4 - SOC 2 CC7.3 KAN-202
it("handles multiple incomplete security events independently", () => {
  const incompleteAlerts = [
    {
      id: 301,
      severity: "high" as const,
      attackType: "Port Scan",
      timestamp: "2026-11-02 18:00",
    },
    {
      id: 302,
      severity: "medium" as const,
      ip: "10.0.0.20",
      attackType: "Suspicious Traffic",
      confidence: 0.81,
    },
  ];

  render(<Alerts alerts={incompleteAlerts} />);

  const alertCards = screen.getAllByRole("article");

  expect(alertCards).toHaveLength(2);

  expect(alertCards[0]).toHaveTextContent("Port Scan");
  expect(alertCards[0]).toHaveTextContent("HIGH");
  expect(alertCards[0]).toHaveTextContent("Source IP: Unavailable");
  expect(alertCards[0]).toHaveTextContent("Port: Unavailable");
  expect(alertCards[0]).toHaveTextContent("AI Confidence: Unavailable");

  expect(alertCards[1]).toHaveTextContent("Suspicious Traffic");
  expect(alertCards[1]).toHaveTextContent("MEDIUM");
  expect(alertCards[1]).toHaveTextContent("Source IP: 10.0.0.20");
  expect(alertCards[1]).toHaveTextContent("Port: Unavailable");
  expect(alertCards[1]).toHaveTextContent("Detected: Unavailable");
  expect(alertCards[1]).toHaveTextContent("AI Confidence: 81%");
});

it("does not display undefined or invalid confidence text for incomplete alerts", () => {
  const incompleteAlerts = [
    {
      id: 303,
      severity: "high" as const,
      attackType: "Port Scan",
    },
    {
      id: 304,
      severity: "low" as const,
      ip: "10.0.0.40",
      port: 53,
      attackType: "Unusual DNS Activity",
      confidence: Number.NaN,
    },
  ];

  render(<Alerts alerts={incompleteAlerts} />);

  expect(screen.queryByText(/undefined/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/NaN%/i)).not.toBeInTheDocument();

  const alertCards = screen.getAllByRole("article");

  expect(alertCards[0]).toHaveTextContent("Detected: Unavailable");
  expect(alertCards[0]).toHaveTextContent("AI Confidence: Unavailable");

  expect(alertCards[1]).toHaveTextContent("AI Confidence: Unavailable");
});