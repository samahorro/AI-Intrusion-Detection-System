import { cleanup, render, screen } from "@testing-library/react";
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
});