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
