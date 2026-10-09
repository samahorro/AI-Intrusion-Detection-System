import {
  describe,
  expect,
  it,
} from "vitest";

import {
  ApiClient,
  ApiClientError,
} from "../apiClient";
import { MockTransport } from "../mockTransport";

import { AuthServiceError } from "./AuthServiceError";
import { BackendAuthService } from "./BackendAuthService";

function createService(
  transport: MockTransport,
) {
  return new BackendAuthService(
    new ApiClient(transport),
  );
}

describe("BackendAuthService", () => {
  it("logs in using the backend username contract", async () => {
    const transport = new MockTransport()
      .when("POST", "/auth/login", (request) => {
        expect(request.body).toEqual({
          username: "robert",
          password: "StrongPassword123!",
        });

        return {
          status: 200,
          data: {
            message: "Login successful.",
            user: {
              id: 7,
              username: "robert",
              created_at: "2026-10-05T00:00:00+00:00",
            },
          },
        };
      });

    const service = createService(transport);

    const session = await service.login({
      username: "  robert  ",
      password: "StrongPassword123!",
    });

    expect(session.user).toEqual({
      id: "7",
      username: "robert",
      displayName: "robert",
      role: "user",
      permissions: [],
    });
  });

  it("restores an authenticated cookie session", async () => {
    const transport = new MockTransport()
      .when("GET", "/auth/me", () => ({
        status: 200,
        data: {
          user: {
            id: 12,
            username: "sessionuser",
          },
        },
      }));

    const service = createService(transport);

    const session =
      await service.getCurrentSession();

    expect(session?.user.username).toBe(
      "sessionuser",
    );
  });

  it("treats a 401 from /auth/me as anonymous", async () => {
    const transport = new MockTransport()
      .when("GET", "/auth/me", () => {
        throw new ApiClientError(401, {
          message: "Authentication required.",
        });
      });

    const service = createService(transport);

    await expect(
      service.getCurrentSession(),
    ).resolves.toBeNull();
  });

  it("maps login 401 responses to invalid credentials", async () => {
    const transport = new MockTransport()
      .when("POST", "/auth/login", () => {
        throw new ApiClientError(401, {
          message: "Invalid username or password.",
        });
      });

    const service = createService(transport);

    try {
      await service.login({
        username: "unknown",
        password: "WrongPassword123!",
      });

      throw new Error("Expected login to fail.");
    } catch (error) {
      expect(error).toBeInstanceOf(
        AuthServiceError,
      );

      expect(
        (error as AuthServiceError).code,
      ).toBe("INVALID_CREDENTIALS");
    }
  });

  it("calls the backend logout endpoint", async () => {
    let logoutCalled = false;

    const transport = new MockTransport()
      .when("POST", "/auth/logout", () => {
        logoutCalled = true;

        return {
          status: 200,
          data: {
            message: "Logout successful.",
          },
        };
      });

    const service = createService(transport);

    await service.logout();

    expect(logoutCalled).toBe(true);
  });
});
