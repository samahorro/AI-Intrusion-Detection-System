import {
  cleanup,
  fireEvent,
  render,
  screen,
  within,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AppShell } from "./AppShell";

afterEach(() => {
  cleanup();
});

describe("AppShell", () => {
  it("renders the brand, primary navigation, and page content", () => {
    render(
      <AppShell currentPath="/dashboard">
        <h1>Testing page</h1>
      </AppShell>,
    );

    expect(screen.getByRole("link", { name: "AI-IDS" })).toHaveAttribute(
      "href",
      "/dashboard",
    );
    expect(screen.getByRole("navigation", { name: "Primary navigation" }))
      .toBeInTheDocument();
    expect(screen.getByRole("main")).toContainElement(
      screen.getByRole("heading", { name: "Testing page" }),
    );
  });

  it("shows the registered primary links but not the login route", () => {
    render(<AppShell currentPath="/dashboard">Content</AppShell>);

    const nav = screen.getByRole("navigation", { name: "Primary navigation" });
    expect(within(nav).getByRole("link", { name: "Dashboard" }))
      .toHaveAttribute("href", "/dashboard");
    expect(within(nav).getByRole("link", { name: "Alerts" }))
      .toHaveAttribute("href", "/alerts");
    expect(within(nav).queryByRole("link", { name: "Sign in" }))
      .not.toBeInTheDocument();
  });

  it("marks the matching navigation link as the current page", () => {
    render(<AppShell currentPath="/alerts">Content</AppShell>);

    expect(screen.getByRole("link", { name: "Alerts" }))
      .toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("link", { name: "Dashboard" }))
      .not.toHaveAttribute("aria-current");
  });

  it("keeps the parent link active for nested paths", () => {
    render(<AppShell currentPath="/alerts/123">Content</AppShell>);

    expect(screen.getByRole("link", { name: "Alerts" }))
      .toHaveAttribute("aria-current", "page");
  });

  it("does not mark a similar prefix as the active route", () => {
    render(<AppShell currentPath="/alerts-archive">Content</AppShell>);

    expect(screen.getByRole("link", { name: "Alerts" }))
      .not.toHaveAttribute("aria-current");
  });

  it("exposes the route owner on navigation links", () => {
    render(<AppShell currentPath="/dashboard">Content</AppShell>);

    expect(screen.getByRole("link", { name: "Dashboard" }))
      .toHaveAttribute("data-route-owner", "kevin");
    expect(screen.getByRole("link", { name: "Account" }))
      .toHaveAttribute("data-route-owner", "robert");
  });

  it("renders an optional user label and header action", () => {
    const onSignOut = vi.fn();
    render(
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
    render(<AppShell currentPath="/dashboard">Content</AppShell>);

    expect(screen.queryByRole("button", { name: "Sign out" }))
      .not.toBeInTheDocument();
    expect(screen.queryByText("Test user")).not.toBeInTheDocument();
  });
});
