import {
  cleanup, fireEvent, render, screen,
} from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it } from "vitest";
import type { AuthSession } from "../../types";
import type { AuthService } from "../../services/auth";
import { AuthProvider } from "./AuthProvider";
import { LoginPage } from "./LoginPage";

const session: AuthSession = {
  user: { id: "12", username: "robert", displayName: "robert", role: "user", permissions: [] },
};

const service: AuthService = {
  async getCurrentSession() { return null; },
  async login() { return session; },
  async logout() { return undefined; },
};

afterEach(() => cleanup());

describe("login return navigation", () => {
  it("returns an authenticated user to their original account page", async () => {
    render(
      <MemoryRouter initialEntries={[{ pathname: "/login", state: { from: "/account", reason: "expired" } }]}>
        <AuthProvider service={service}>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/account" element={<p>Account destination</p>} />
            <Route path="/console" element={<p>Console destination</p>} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>,
    );
    expect(await screen.findByText(/Your session expired/)).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText(/Username/), { target: { value: "robert" } });
    fireEvent.change(screen.getByLabelText(/Password/), { target: { value: "Password123!" } });
    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));
    expect(await screen.findByText("Account destination")).toBeInTheDocument();
  });
});
