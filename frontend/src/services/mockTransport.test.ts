import { describe, expect, it } from "vitest";

import { MockTransport } from "./mockTransport";

describe("MockTransport", () => {
  it("returns the registered response for a method and path", async () => {
    const transport = new MockTransport();
    transport.when("GET", "/health", () => ({
      status: 200,
      data: { status: "healthy" },
    }));

    await expect(
      transport.request<{ status: string }>({ method: "GET", path: "/health" }),
    ).resolves.toEqual({ status: 200, data: { status: "healthy" } });
  });

  it("keeps handlers for different HTTP methods separate", async () => {
    const transport = new MockTransport()
      .when("GET", "/records", () => ({ status: 200, data: ["first"] }))
      .when("POST", "/records", () => ({ status: 201, data: ["created"] }));

    const read = await transport.request<string[]>({ method: "GET", path: "/records" });
    const create = await transport.request<string[]>({ method: "POST", path: "/records" });

    expect(read.data).toEqual(["first"]);
    expect(create.status).toBe(201);
    expect(create.data).toEqual(["created"]);
  });

  it("passes the request body and headers to an asynchronous handler", async () => {
    const transport = new MockTransport().when("POST", "/analyze", async (request) => {
      await Promise.resolve();
      return { status: 200, data: { input: request.body, headers: request.headers } };
    });
    const body = { flowId: "flow-123" };
    const headers = { "X-Test": "integration" };

    const result = await transport.request({
      method: "POST",
      path: "/analyze",
      body,
      headers,
    });

    expect(result.data).toEqual({ input: body, headers });
  });

  it("fails clearly when no handler matches the requested method and path", async () => {
    const transport = new MockTransport().when("GET", "/health", () => ({
      status: 200,
      data: null,
    }));

    await expect(
      transport.request({ method: "POST", path: "/health" }),
    ).rejects.toThrow("No mock handler registered for POST /health");
    await expect(
      transport.request({ method: "GET", path: "/missing" }),
    ).rejects.toThrow("No mock handler registered for GET /missing");
  });
});
