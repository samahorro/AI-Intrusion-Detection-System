import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { MemoryRouter } from "react-router-dom";

import type { AuthService } from "../services/auth";
import { AuthProvider } from "../features/auth";
import { ProfileMenu } from "./ProfileMenu";

const service: AuthService = {
  async login() { throw new Error("Not needed in this test"); },
  async logout() { return undefined; },
  async getCurrentSession() {
    return {
      user: {
        id: "17",
        username: "actual_user",
        displayName: "actual_user",
        role: "user",
        permissions: [],
      },
    };
  },
};

afterEach(cleanup);

describe("ProfileMenu", () => {
  it("uses the signed-in username and exposes the Account route", async () => {
    render(
      <MemoryRouter>
        <AuthProvider service={service}>
          <ProfileMenu />
        </AuthProvider>
      </MemoryRouter>,
    );

    expect(await screen.findByText("actual_user")).toBeInTheDocument();
    expect(screen.queryByText("demo_user")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Account menu" }));
    expect(screen.getByRole("link", { name: "View account" }))
      .toHaveAttribute("href", "/account");
  });
});
