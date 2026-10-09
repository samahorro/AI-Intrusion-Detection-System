import {
  cleanup,
  render,
  screen,
} from "@testing-library/react";

import {
  MemoryRouter,
  Route,
  Routes,
} from "react-router-dom";

import {
  afterEach,
  describe,
  expect,
  it,
} from "vitest";

import type {
  AuthSession,
} from "../../types";
import type {
  AuthService,
} from "../../services/auth";

import { AuthProvider } from "./AuthProvider";
import { ProtectedRoute } from "./ProtectedRoute";

const AUTHENTICATED_SESSION: AuthSession = {
  user: {
    id: "7",
    username: "robert",
    displayName: "robert",
    role: "user",
    permissions: [],
  },
};

function createService(
  session: AuthSession | null,
): AuthService {
  return {
    async login() {
      if (!session) {
        throw new Error("No test session configured.");
      }

      return session;
    },

    async logout() {
      return undefined;
    },

    async getCurrentSession() {
      return session;
    },
  };
}

function renderProtectedRoute(
  service: AuthService,
) {
  return render(
    <MemoryRouter
      initialEntries={["/dashboard"]}
    >
      <AuthProvider service={service}>
        <Routes>
          <Route
            path="/login"
            element={<p>Login target</p>}
          />

          <Route
            path="/dashboard"
            element={(
              <ProtectedRoute>
                <p>Protected dashboard</p>
              </ProtectedRoute>
            )}
          />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  );
}

afterEach(() => {
  cleanup();
});

describe("ProtectedRoute", () => {
  it("redirects anonymous users to login", async () => {
    renderProtectedRoute(
      createService(null),
    );

    expect(
      await screen.findByText("Login target"),
    ).toBeInTheDocument();
  });

  it("renders protected content for an authenticated session", async () => {
    renderProtectedRoute(
      createService(AUTHENTICATED_SESSION),
    );

    expect(
      await screen.findByText(
        "Protected dashboard",
      ),
    ).toBeInTheDocument();
  });
});
