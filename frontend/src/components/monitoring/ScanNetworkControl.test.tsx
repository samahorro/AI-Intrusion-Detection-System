import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import ScanNetworkControl from "./ScanNetworkControl";

const mocks = vi.hoisted(() => ({
  getInterfaces: vi.fn(),
  getStatus: vi.fn(),
  start: vi.fn(),
  stop: vi.fn(),
}));

vi.mock("../../services/captureService", () => ({
  captureService: {
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

describe("ScanNetworkControl", () => {
  it("loads interfaces and renders the ready state", async () => {
    render(<ScanNetworkControl />);

    expect(
      screen.getByRole("button", { name: /please wait/i }),
    ).toBeDisabled();

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /scan network/i }),
      ).toBeEnabled();
    });

    expect(
      screen.getByRole("combobox", { name: /network interface/i }),
    ).toHaveValue("Wi-Fi");

    expect(screen.getByText("Capture stopped")).toBeInTheDocument();
  });

  it("starts capture when Scan Network is clicked", async () => {
    render(<ScanNetworkControl />);

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /scan network/i }),
      ).toBeEnabled();
    });

    fireEvent.click(
      screen.getByRole("button", { name: /scan network/i }),
    );

    await waitFor(() => {
      expect(mocks.start).toHaveBeenCalledWith("Wi-Fi");
    });
  });

  it("shows Stop Scan when capture is already running", async () => {
    mocks.getStatus.mockResolvedValue({
      running: true,
      interface: "Wi-Fi",
    });

    render(<ScanNetworkControl />);

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /stop scan/i }),
      ).toBeInTheDocument();
    });

    expect(
      screen.getByText("TShark capture process running"),
    ).toBeInTheDocument();
  });
});