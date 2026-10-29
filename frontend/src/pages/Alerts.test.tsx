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