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

// Sprint 4 - SOC 2 CC7.3 KAN-203
it("maps security event data to the correct frontend alert fields", () => {
  const sourceEvent = [
    {
      id: 401,
      severity: "critical" as const,
      ip: "172.16.10.25",
      port: 3389,
      attackType: "Brute Force",
      timestamp: "2026-11-02 19:30",
      confidence: 0.97,
    },
  ];

  render(<Alerts alerts={sourceEvent} />);

  const alertCard = screen.getByRole("article");

  expect(alertCard).toHaveTextContent("CRITICAL");
  expect(alertCard).toHaveTextContent("Brute Force");
  expect(alertCard).toHaveTextContent(
    "Source IP: 172.16.10.25",
  );
  expect(alertCard).toHaveTextContent("Port: 3389");
  expect(alertCard).toHaveTextContent(
    "Detected: 2026-11-02 19:30",
  );
  expect(alertCard).toHaveTextContent(
    "AI Confidence: 97%",
  );
});

it("does not swap security event fields during presentation", () => {
  const sourceEvent = [
    {
      id: 402,
      severity: "medium" as const,
      ip: "10.20.30.40",
      port: 8080,
      attackType: "Suspicious Traffic",
      timestamp: "2026-11-02 20:00",
      confidence: 0.73,
    },
  ];

  render(<Alerts alerts={sourceEvent} />);

  const alertCard = screen.getByRole("article");

  expect(alertCard).toHaveTextContent(
    "Source IP: 10.20.30.40",
  );
  expect(alertCard).toHaveTextContent("Port: 8080");
  expect(alertCard).toHaveTextContent(
    "Detected: 2026-11-02 20:00",
  );
  expect(alertCard).toHaveTextContent(
    "AI Confidence: 73%",
  );

  expect(alertCard).not.toHaveTextContent(
    "Source IP: 8080",
  );
  expect(alertCard).not.toHaveTextContent(
    "Port: 10.20.30.40",
  );
});

// Sprint 4 - SOC 2 CC7.3 KAN-204
it("presents all supported severity levels correctly", () => {
  const testAlerts = [
    {
      id: 501,
      severity: "low" as const,
      ip: "10.0.0.1",
      port: 53,
      attackType: "Low Severity Event",
      timestamp: "2026-11-02 20:10",
      confidence: 0.25,
    },
    {
      id: 502,
      severity: "medium" as const,
      ip: "10.0.0.2",
      port: 443,
      attackType: "Medium Severity Event",
      timestamp: "2026-11-02 20:11",
      confidence: 0.5,
    },
    {
      id: 503,
      severity: "high" as const,
      ip: "10.0.0.3",
      port: 22,
      attackType: "High Severity Event",
      timestamp: "2026-11-02 20:12",
      confidence: 0.75,
    },
    {
      id: 504,
      severity: "critical" as const,
      ip: "10.0.0.4",
      port: 3389,
      attackType: "Critical Severity Event",
      timestamp: "2026-11-02 20:13",
      confidence: 0.99,
    },
  ];

  render(<Alerts alerts={testAlerts} />);

  const alertCards = screen.getAllByRole("article");

  expect(alertCards[0]).toHaveTextContent("LOW");
  expect(alertCards[1]).toHaveTextContent("MEDIUM");
  expect(alertCards[2]).toHaveTextContent("HIGH");
  expect(alertCards[3]).toHaveTextContent("CRITICAL");
});

it("formats confidence values as understandable percentages", () => {
  const testAlerts = [
    {
      id: 505,
      severity: "low" as const,
      ip: "10.0.0.5",
      port: 80,
      attackType: "Zero Confidence Event",
      timestamp: "2026-11-02 20:20",
      confidence: 0,
    },
    {
      id: 506,
      severity: "high" as const,
      ip: "10.0.0.6",
      port: 22,
      attackType: "High Confidence Event",
      timestamp: "2026-11-02 20:21",
      confidence: 0.94,
    },
    {
      id: 507,
      severity: "critical" as const,
      ip: "10.0.0.7",
      port: 3389,
      attackType: "Maximum Confidence Event",
      timestamp: "2026-11-02 20:22",
      confidence: 1,
    },
  ];

  render(<Alerts alerts={testAlerts} />);

  const alertCards = screen.getAllByRole("article");

  expect(alertCards[0]).toHaveTextContent("AI Confidence: 0%");
  expect(alertCards[1]).toHaveTextContent("AI Confidence: 94%");
  expect(alertCards[2]).toHaveTextContent("AI Confidence: 100%");
});

it("does not present invalid confidence values as legitimate percentages", () => {
  const testAlerts = [
    {
      id: 508,
      severity: "medium" as const,
      ip: "10.0.0.8",
      port: 443,
      attackType: "Invalid Confidence Event",
      timestamp: "2026-11-02 20:30",
      confidence: -0.5,
    },
    {
      id: 509,
      severity: "high" as const,
      ip: "10.0.0.9",
      port: 22,
      attackType: "Out of Range Confidence Event",
      timestamp: "2026-11-02 20:31",
      confidence: 1.5,
    },
  ];

  render(<Alerts alerts={testAlerts} />);

  const alertCards = screen.getAllByRole("article");

  expect(alertCards[0]).toHaveTextContent(
    "AI Confidence: Unavailable",
  );

  expect(alertCards[1]).toHaveTextContent(
    "AI Confidence: Unavailable",
  );

  expect(screen.queryByText("-50%")).not.toBeInTheDocument();
  expect(screen.queryByText("150%")).not.toBeInTheDocument();
});