import {
  afterEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import { ApiClientError } from "./apiClient";
import { FetchTransport } from "./fetchTransport";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("FetchTransport", () => {
  it("includes browser credentials for cookie sessions", async () => {
    const fetchMock = vi.fn(async () => (
      new Response(
        JSON.stringify({ status: "ok" }),
        {
          status: 200,
          headers: {
            "Content-Type": "application/json",
          },
        },
      )
    ));

    vi.stubGlobal("fetch", fetchMock);

    const transport = new FetchTransport({
      baseUrl: "http://localhost:8000",
    });

    await transport.request({
      method: "GET",
      path: "/auth/me",
    });

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/auth/me",
      expect.objectContaining({
        method: "GET",
        credentials: "include",
      }),
    );
  });

  it("surfaces FastAPI detail messages", async () => {
    const fetchMock = vi.fn(async () => (
      new Response(
        JSON.stringify({
          detail: "Authentication required.",
        }),
        {
          status: 401,
          headers: {
            "Content-Type": "application/json",
          },
        },
      )
    ));

    vi.stubGlobal("fetch", fetchMock);

    const transport = new FetchTransport({
      baseUrl: "http://localhost:8000",
    });

    try {
      await transport.request({
        method: "GET",
        path: "/auth/me",
      });

      throw new Error("Expected request to fail.");
    } catch (error) {
      expect(error).toBeInstanceOf(
        ApiClientError,
      );

      expect(
        (error as ApiClientError).message,
      ).toBe("Authentication required.");
    }
  });
});

// Authentication expiration must be triggered only by a protected resource 401.
// /auth/me is an ordinary startup probe and /auth/login can reject bad passwords.
import { subscribeToSessionExpiry } from "./auth/sessionExpiryEvents";

describe("FetchTransport auth invalidation", () => {
  it("emits session expiration on protected resource 401", async () => {
    const onExpired = vi.fn();
    const unsubscribe = subscribeToSessionExpiry(onExpired);
    vi.stubGlobal("fetch", vi.fn(async () => new Response("{}", {
      status: 401,
      headers: { "Content-Type": "application/json" },
    })));
    try {
      const client = new FetchTransport({ baseUrl: "http://localhost:8000" });
      await expect(client.request({ method: "GET", path: "/capture/stats" }))
        .rejects.toBeInstanceOf(ApiClientError);
      expect(onExpired).toHaveBeenCalledTimes(1);
    } finally {
      unsubscribe();
    }
  });

  it("expires the session even if the 401 body is malformed JSON", async () => {
    const onExpired = vi.fn();
    const unsubscribe = subscribeToSessionExpiry(onExpired);
    vi.stubGlobal("fetch", vi.fn(async () => new Response("invalid json", {
      status: 401,
      headers: { "Content-Type": "application/json" },
    })));
    try {
      const client = new FetchTransport({ baseUrl: "http://localhost:8000" });
      await expect(client.request({ method: "GET", path: "/capture/stats" }))
        .rejects.toThrow();
      expect(onExpired).toHaveBeenCalledTimes(1);
    } finally {
      unsubscribe();
    }
  });

  it("does not expire a session on a failed login or session probe", async () => {
    const onExpired = vi.fn();
    const unsubscribe = subscribeToSessionExpiry(onExpired);
    vi.stubGlobal("fetch", vi.fn(async () => new Response("{}", {
      status: 401,
      headers: { "Content-Type": "application/json" },
    })));
    try {
      const client = new FetchTransport({ baseUrl: "http://localhost:8000" });
      for (const path of ["/auth/login", "/auth/me", "/auth/logout"]) {
        await expect(client.request({ method: "GET", path }))
          .rejects.toBeInstanceOf(ApiClientError);
      }
      expect(onExpired).not.toHaveBeenCalled();
    } finally {
      unsubscribe();
    }
  });
});
