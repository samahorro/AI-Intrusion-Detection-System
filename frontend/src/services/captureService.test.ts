import { afterEach, describe, expect, it, vi } from "vitest";
import { captureService } from "./captureService";
import { subscribeToSessionExpiry } from "./auth/sessionExpiryEvents";

afterEach(() => vi.unstubAllGlobals());

describe("captureService session handling", () => {
  it("reports a 401 on protected capture requests", async () => {
    const observer = vi.fn();
    const off = subscribeToSessionExpiry(observer);
    vi.stubGlobal("fetch", vi.fn(async () => new Response(
      JSON.stringify({ detail: "Authentication required" }),
      { status: 401, headers: { "Content-Type": "application/json" } },
    )));
    try {
      await expect(captureService.getStats()).rejects.toThrow("Authentication required");
      expect(observer).toHaveBeenCalledTimes(1);
    } finally {
      off();
    }
  });

  it("does not expire a session on server errors or missing endpoints", async () => {
    const observer = vi.fn();
    const off = subscribeToSessionExpiry(observer);
    vi.stubGlobal("fetch", vi.fn(async () => new Response("{}", {
      status: 503, headers: { "Content-Type": "application/json" },
    })));
    try {
      await expect(captureService.getStats()).rejects.toThrow("Request failed: 503");
      expect(observer).not.toHaveBeenCalled();
    } finally {
      off();
    }
  });

  it("reports a missing experimental predictions endpoint without mock success", async () => {
    const observer = vi.fn();
    const off = subscribeToSessionExpiry(observer);
    vi.stubGlobal("fetch", vi.fn(async () => new Response("{}", { status: 404 })));
    try {
      await expect(captureService.getExperimentalPredictions())
        .rejects.toThrow("backend/ML integration is still pending");
      expect(observer).not.toHaveBeenCalled();
    } finally {
      off();
    }
  });

  it("keeps session state unchanged on network failure", async () => {
    const observer = vi.fn();
    const off = subscribeToSessionExpiry(observer);
    vi.stubGlobal("fetch", vi.fn(async () => { throw new TypeError("offline"); }));
    try {
      await expect(captureService.getStats()).rejects.toThrow("offline");
      expect(observer).not.toHaveBeenCalled();
    } finally {
      off();
    }
  });
});
