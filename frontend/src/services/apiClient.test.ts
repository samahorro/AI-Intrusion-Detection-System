import { describe, expect, it } from "vitest";

import type { ApiRequest, ApiResponse } from "../types";
import {
  ApiClient,
  ApiClientError,
  type ApiTransport,
} from "./apiClient";

function createRecordingClient() {
  const requests: ApiRequest[] = [];
  const transport: ApiTransport = {
    async request<T>(request: ApiRequest): Promise<ApiResponse<T>> {
      requests.push(request);
      return {
        status: 202,
        data: { acknowledged: true } as T,
      };
    },
  };

  return {
    client: new ApiClient(transport),
    requests,
  };
}

describe("ApiClient request forwarding", () => {
  it("forwards GET and DELETE paths and headers without a body", async () => {
    const { client, requests } = createRecordingClient();
    const headers = { "X-Request-ID": "test-123" };

    const getResult = await client.get("/health", headers);
    const deleteResult = await client.delete("/sessions/1", headers);

    expect(getResult).toEqual({ status: 202, data: { acknowledged: true } });
    expect(deleteResult.status).toBe(202);
    expect(requests).toEqual([
      { method: "GET", path: "/health", headers },
      { method: "DELETE", path: "/sessions/1", headers },
    ]);
  });

  it("forwards POST, PUT, and PATCH bodies without altering them", async () => {
    const { client, requests } = createRecordingClient();
    const postBody = { username: "test_user" };
    const putBody = { enabled: true };
    const patchBody = { enabled: false };

    await client.post("/users", postBody, { "X-Test": "post" });
    await client.put("/settings", putBody);
    await client.patch("/settings", patchBody);

    expect(requests).toEqual([
      {
        method: "POST",
        path: "/users",
        body: postBody,
        headers: { "X-Test": "post" },
      },
      { method: "PUT", path: "/settings", body: putBody, headers: undefined },
      { method: "PATCH", path: "/settings", body: patchBody, headers: undefined },
    ]);
    expect(postBody).toEqual({ username: "test_user" });
  });

  it("propagates a transport failure instead of treating it as success", async () => {
    const failure = new ApiClientError(503, { message: "Service unavailable" });
    const transport: ApiTransport = {
      async request<T>(): Promise<ApiResponse<T>> {
        throw failure;
      },
    };

    await expect(new ApiClient(transport).get("/health")).rejects.toBe(failure);
  });
});

describe("ApiClientError", () => {
  it("retains backend error code and structured details", () => {
    const error = new ApiClientError(409, {
      message: "Username already exists",
      code: "USER_EXISTS",
      details: { field: "username" },
    });

    expect(error).toBeInstanceOf(Error);
    expect(error.name).toBe("ApiClientError");
    expect(error.status).toBe(409);
    expect(error.message).toBe("Username already exists");
    expect(error.code).toBe("USER_EXISTS");
    expect(error.details).toEqual({ field: "username" });
  });

  it("falls back to a status-based message when no message is supplied", () => {
    const error = new ApiClientError(401, {
      code: "AUTH_REQUIRED",
    });

    expect(error.message).toBe("Request failed with status 401");
    expect(error.code).toBe("AUTH_REQUIRED");
    expect(error.details).toBeUndefined();
  });

  it("preserves structured validation details and handles an empty payload", () => {
    const details = [{ field: "username", reason: "Required" }];
    const validationError = new ApiClientError(422, { details });
    const genericError = new ApiClientError(500);

    expect(validationError.message).toBe("Request failed with status 422");
    expect(validationError.details).toEqual(details);
    expect(genericError.message).toBe("Request failed with status 500");
    expect(genericError.details).toBeUndefined();
  });
});
