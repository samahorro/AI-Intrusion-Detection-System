import {
  act, cleanup, fireEvent, render, screen, waitFor,
} from "@testing-library/react";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";
import { afterEach, describe, expect, it } from "vitest";
import type { AuthSession } from "../../types";
import type { AuthService } from "../../services/auth";
import { reportSessionExpiry } from "../../services/auth/sessionExpiryEvents";
import { AuthProvider } from "./AuthProvider";
import { ProtectedRoute } from "./ProtectedRoute";
import { useAuth } from "./useAuth";

const session: AuthSession = {
  user: { id: "7", username: "robert", displayName: "robert", role: "user", permissions: [] },
};

function serviceWithGet(getCurrentSession: AuthService["getCurrentSession"]): AuthService {
  return {
    getCurrentSession,
    async login() { return session; },
    async logout() { return undefined; },
  };
}

function LoginDestination() {
  const location = useLocation();
  const state = location.state as { from?: string; reason?: string } | null;
  return <div>Login target: {state?.from ?? "none"}; {state?.reason ?? "none"}</div>;
}

function SessionRefreshButton() {
  const { refreshSession } = useAuth();
  return <button type="button" onClick={() => { void refreshSession(); }}>Refresh session</button>;
}

function renderAccount(service: AuthService, showRefreshButton = false) {
  return render(
    <MemoryRouter initialEntries={["/account"]}>
      <AuthProvider service={service}>
        <Routes>
          <Route path="/login" element={<LoginDestination />} />
          <Route path="/account" element={(
            <ProtectedRoute>
              <p>Private account content</p>
              {showRefreshButton && <SessionRefreshButton />}
            </ProtectedRoute>
          )} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  );
}

afterEach(() => cleanup());

describe("session expiration and recovery", () => {
  it("shows a retry instead of logging out on an authentication network outage", async () => {
    let checks = 0;
    const service = serviceWithGet(async () => {
      checks += 1;
      if (checks === 1) throw new TypeError("Network unavailable");
      return session;
    });
    renderAccount(service);
    expect(await screen.findByText("Unable to verify your session")).toBeInTheDocument();
    expect(screen.queryByText(/Login target/)).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Retry session check" }));
    expect(await screen.findByText("Private account content")).toBeInTheDocument();
    expect(checks).toBe(2);
  });

  it("revokes protected UI and preserves its destination on a verified 401", async () => {
    renderAccount(serviceWithGet(async () => session));
    expect(await screen.findByText("Private account content")).toBeInTheDocument();
    act(() => reportSessionExpiry());
    expect(await screen.findByText("Login target: /account; expired")).toBeInTheDocument();
  });

  it("ignores a late refresh response after a confirmed expiration", async () => {
    let checks = 0;
    let finishRefresh: ((s: AuthSession) => void) | undefined;
    const service = serviceWithGet(() => {
      checks += 1;
      if (checks === 1) return Promise.resolve(session);
      return new Promise<AuthSession>((resolve) => { finishRefresh = resolve; });
    });
    renderAccount(service, true);
    expect(await screen.findByText("Private account content")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Refresh session" }));
    expect(await screen.findByText("Checking your AI-IDS session...")).toBeInTheDocument();
    act(() => reportSessionExpiry());
    expect(await screen.findByText("Login target: /account; expired")).toBeInTheDocument();
    await act(async () => { finishRefresh?.(session); });
    await waitFor(() => {
      expect(screen.queryByText("Private account content")).not.toBeInTheDocument();
    });
  });
});
