import {
  cleanup,
  fireEvent,
  render,
  screen,
  within,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter } from "react-router-dom";
import type { ReactElement } from "react";

import { AppShell } from "./AppShell";

afterEach(() => {
  cleanup();
});

function renderShell(ui: ReactElement) {
  return render(<MemoryRouter>{ui}</MemoryRouter>);
}

describe("AppShell", () => {
  it("renders the brand, primary navigation, and page content", () => {
    renderShell(
      <AppShell currentPath="/dashboard">
        <h1>Testing page</h1>
      </AppShell>,
    );

    expect(screen.getByRole("link", { name: "AI-IDS" })).toHaveAttribute(
      "href",
      "/console",
    );
    expect(screen.getByRole("navigation", { name: "Primary navigation" }))
      .toBeInTheDocument();
    expect(screen.getByRole("main")).toContainElement(
      screen.getByRole("heading", { name: "Testing page" }),
    );
  });

  it("shows the registered primary links but not the login route", () => {
    renderShell(<AppShell currentPath="/dashboard">Content</AppShell>);

    const nav = screen.getByRole("navigation", { name: "Primary navigation" });
    expect(within(nav).getByRole("link", { name: "Dashboard" }))
      .toHaveAttribute("href", "/dashboard");
    expect(within(nav).getByRole("link", { name: "Alerts" }))
      .toHaveAttribute("href", "/alerts");
    expect(within(nav).getByRole("link", { name: "Security Console" }))
      .toHaveAttribute("href", "/console");
    expect(within(nav).getByRole("link", { name: "Account" }))
      .toHaveAttribute("href", "/account");
    expect(within(nav).queryByRole("link", { name: "Users" }))
      .not.toBeInTheDocument();
    expect(within(nav).queryByRole("link", { name: "Sign in" }))
      .not.toBeInTheDocument();
  });

  it("marks the matching navigation link as the current page", () => {
    renderShell(<AppShell currentPath="/alerts">Content</AppShell>);

    expect(screen.getByRole("link", { name: "Alerts" }))
      .toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("link", { name: "Dashboard" }))
      .not.toHaveAttribute("aria-current");
  });

  it("keeps the parent link active for nested paths", () => {
    renderShell(<AppShell currentPath="/alerts/123">Content</AppShell>);

    expect(screen.getByRole("link", { name: "Alerts" }))
      .toHaveAttribute("aria-current", "page");
  });

  it("does not mark a similar prefix as the active route", () => {
    renderShell(<AppShell currentPath="/alerts-archive">Content</AppShell>);

    expect(screen.getByRole("link", { name: "Alerts" }))
      .not.toHaveAttribute("aria-current");
  });

  it("exposes the route owner on navigation links", () => {
    renderShell(<AppShell currentPath="/dashboard">Content</AppShell>);

    expect(screen.getByRole("link", { name: "Dashboard" }))
      .toHaveAttribute("data-route-owner", "kevin");
    expect(screen.getByRole("link", { name: "Account" }))
      .toHaveAttribute("data-route-owner", "robert");
  });

  it("can omit the wrapper main landmark when a page already supplies one", () => {
    renderShell(
      <AppShell currentPath="/dashboard" contentTag="div">
        <main><h1>Dashboard content</h1></main>
      </AppShell>,
    );
    expect(screen.getAllByRole("main")).toHaveLength(1);
  });

  it("renders an optional user label and header action", () => {
    const onSignOut = vi.fn();
    renderShell(
      <AppShell
        currentPath="/dashboard"
        userLabel="Test user"
        headerActions={<button onClick={onSignOut}>Sign out</button>}
      >
        Content
      </AppShell>,
    );

    expect(screen.getByText("Test user")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Sign out" }));
    expect(onSignOut).toHaveBeenCalledOnce();
  });

  it("does not render optional header utilities when they are omitted", () => {
    renderShell(<AppShell currentPath="/dashboard">Content</AppShell>);

    expect(screen.queryByRole("button", { name: "Sign out" }))
      .not.toBeInTheDocument();
    expect(screen.queryByText("Test user")).not.toBeInTheDocument();
  });
});
