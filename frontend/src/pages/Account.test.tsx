
import {
  cleanup,
  render,
  screen,
} from "@testing-library/react";

import {
  afterEach,
  describe,
  expect,
  it,
} from "vitest";

import {
  MemoryRouter,
  Route,
  Routes,
} from "react-router-dom";

import type { AuthSession } from "../types";
import type { AuthService } from "../services/auth";

import {
  AuthProvider,
  ProtectedRoute,
} from "../features/auth";

import Account from "./Account";

// ============================================================
// Mock Authenticated User Session
// ============================================================

const knownSession: AuthSession = {
  user: {
    id: "17",
    username: "robert",
    displayName: "robert",
    role: "user",
    permissions: [],
    createdAt: "2026-10-05T00:00:00+00:00",
  },
};

// ============================================================
// Account Page Test Renderer
// ============================================================

function renderAccount(session: AuthSession | null) {
  const service: AuthService = {
    async login() {
      throw new Error("Not needed in this test");
    },

    async logout() {
      return undefined;
    },

    async getCurrentSession() {
      return session;
    },
  };

  return render(
    <MemoryRouter initialEntries={["/account"]}>
      <AuthProvider service={service}>
        <Routes>
          <Route
            path="/login"
            element={<p>Sign-in page</p>}
          />

          <Route
            path="/account"
            element={
              <ProtectedRoute>
                <Account />
              </ProtectedRoute>
            }
          />

          <Route
            path="/console"
            element={<p>Security Console page</p>}
          />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  );
}

// Clean up rendered components between tests.
afterEach(cleanup);

// ============================================================
// AEGIS Account Overview Tests
// ============================================================

describe("Account page", () => {
  // ----------------------------------------------------------
  // Authenticated User Information
  // ----------------------------------------------------------

  it(
    "shows real session details and an explicit read-only notice",
    async () => {
      renderAccount(knownSession);

      // Verify the updated Account Overview heading.
      expect(
        await screen.findByRole("heading", {
          name: "Account Overview",
          level: 1,
        }),
      ).toBeInTheDocument();

      // Verify that the authenticated username is shown.
      expect(
        screen.getAllByText("robert").length,
      ).toBeGreaterThan(0);

      // Verify that the account ID comes from the session.
      expect(
        screen.getByText("17"),
      ).toBeInTheDocument();

      // Verify that the account creation date is correct.
      expect(
        screen.getByText("October 5, 2026"),
      ).toBeInTheDocument();

      // Verify the new profile information section.
      expect(
        screen.getByRole("region", {
          name: "Profile information",
        }),
      ).toBeInTheDocument();

      // Verify the account is marked read-only.
      expect(
        screen.getByText("READ ONLY"),
      ).toBeInTheDocument();

      // Verify the updated read-only explanation.
      expect(
        screen.getByText(
          /Account details are managed by AEGIS and cannot be edited from this page/i,
        ),
      ).toBeInTheDocument();

      // Ensure no unsupported account editing controls exist.
      expect(
        screen.queryByRole("button", {
          name: /save/i,
        }),
      ).not.toBeInTheDocument();
    },
  );

  // ----------------------------------------------------------
  // Missing Account Creation Date
  // ----------------------------------------------------------

  it(
    "does not invent a missing account creation date",
    async () => {
      renderAccount({
        user: {
          ...knownSession.user,
          createdAt: undefined,
        },
      });

      expect(
        await screen.findByText("Not available"),
      ).toBeInTheDocument();
    },
  );

  // ----------------------------------------------------------
  // Unauthenticated User Redirect
  // ----------------------------------------------------------

  it(
    "redirects guests without exposing account information",
    async () => {
      renderAccount(null);

      expect(
        await screen.findByText("Sign-in page"),
      ).toBeInTheDocument();

      // No authenticated user information should leak.
      expect(
        screen.queryByText("17"),
      ).not.toBeInTheDocument();

      expect(
        screen.queryByRole("heading", {
          name: "Account Overview",
        }),
      ).not.toBeInTheDocument();
    },
  );

  // ----------------------------------------------------------
  // Navigation Back to Security Console
  // ----------------------------------------------------------

  it(
    "provides a working navigation link to the Security Console",
    async () => {
      renderAccount(knownSession);

      const backLink = await screen.findByRole("link", {
        name: /Back to Security Console/i,
      });

      expect(backLink).toHaveAttribute(
        "href",
        "/console",
      );
    },
  );
});
