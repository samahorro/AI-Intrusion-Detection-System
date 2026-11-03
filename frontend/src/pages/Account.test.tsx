import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import type { AuthSession } from "../types";
import type { AuthService } from "../services/auth";
import { AuthProvider, ProtectedRoute } from "../features/auth";
import Account from "./Account";

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

function renderAccount(session: AuthSession | null) {
  const service: AuthService = {
    async login() { throw new Error("Not needed in this test"); },
    async logout() { return undefined; },
    async getCurrentSession() { return session; },
  };

  return render(
    <MemoryRouter initialEntries={["/account"]}>
      <AuthProvider service={service}>
        <Routes>
          <Route path="/login" element={<p>Sign-in page</p>} />
          <Route
            path="/account"
            element={<ProtectedRoute><Account /></ProtectedRoute>}
          />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  );
}

afterEach(cleanup);

describe("Account page", () => {
  it("shows real session details and an explicit read-only notice", async () => {
    renderAccount(knownSession);
    expect(await screen.findByRole("heading", { name: "Your account" }))
      .toBeInTheDocument();
    expect(screen.getByText("17")).toBeInTheDocument();
    expect(screen.getAllByText("robert").length).toBeGreaterThan(0);
    expect(screen.getByText("October 5, 2026")).toBeInTheDocument();
    expect(screen.getByText(/Profile information is read-only/))
      .toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /save/i }))
      .not.toBeInTheDocument();
  });

  it("does not invent a missing account creation date", async () => {
    renderAccount({
      user: { ...knownSession.user, createdAt: undefined },
    });
    expect(await screen.findByText("Not available")).toBeInTheDocument();
  });

  it("redirects guests without exposing account information", async () => {
    renderAccount(null);
    expect(await screen.findByText("Sign-in page")).toBeInTheDocument();
    expect(screen.queryByText("17")).not.toBeInTheDocument();
  });
});
