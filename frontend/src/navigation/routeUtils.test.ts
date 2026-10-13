import { describe, expect, it } from "vitest";

import { appRouteRegistry } from "./routeRegistry";
import {
  getPrimaryNavigationRoutes,
  getProtectedRoutes,
  getRouteByPath,
  getRoutesByOwner,
  isMonitoringRoute,
  isRobertOwnedRoute,
  isRouteActive,
} from "./routeUtils";

describe("route registry and navigation helpers", () => {
  it("maintains unique route IDs and paths", () => {
    const ids = appRouteRegistry.map((route) => route.id);
    const paths = appRouteRegistry.map((route) => route.path);

    expect(new Set(ids).size).toBe(ids.length);
    expect(new Set(paths).size).toBe(paths.length);
  });

  it("looks up a known route by its exact path", () => {
    expect(getRouteByPath("/dashboard")).toMatchObject({
      id: "dashboard",
      owner: "kevin",
      requiresAuth: true,
    });
  });

  it("does not incorrectly match nested or unknown paths", () => {
    expect(getRouteByPath("/dashboard/details")).toBeUndefined();
    expect(getRouteByPath("/does-not-exist")).toBeUndefined();
  });

  it("returns only routes belonging to the specified owner", () => {
    const robertRoutes = getRoutesByOwner("robert");
    const kevinRoutes = getRoutesByOwner("kevin");

    expect(robertRoutes.length).toBeGreaterThan(0);
    expect(kevinRoutes.length).toBeGreaterThan(0);
    expect(robertRoutes.every((route) => route.owner === "robert")).toBe(true);
    expect(kevinRoutes.every((route) => route.owner === "kevin")).toBe(true);
  });

  it("selects only routes flagged for primary navigation", () => {
    const routes = getPrimaryNavigationRoutes();

    expect(routes.every((route) => route.showInPrimaryNavigation)).toBe(true);
    expect(routes.some((route) => route.path === "/login")).toBe(false);
    expect(routes.some((route) => route.path === "/dashboard")).toBe(true);
  });

  it("selects only protected routes and excludes login", () => {
    const routes = getProtectedRoutes();

    expect(routes.every((route) => route.requiresAuth)).toBe(true);
    expect(routes.some((route) => route.path === "/login")).toBe(false);
    expect(routes.some((route) => route.path === "/alerts")).toBe(true);
  });

  it("identifies Kevin-owned monitoring routes", () => {
    expect(isMonitoringRoute("/dashboard")).toBe(true);
    expect(isMonitoringRoute("/alerts")).toBe(true);
    expect(isMonitoringRoute("/account")).toBe(false);
    expect(isMonitoringRoute("/unknown")).toBe(false);
  });

  it("identifies Robert-owned routes without claiming Kevin routes", () => {
    expect(isRobertOwnedRoute("/login")).toBe(true);
    expect(isRobertOwnedRoute("/account")).toBe(true);
    expect(isRobertOwnedRoute("/dashboard")).toBe(false);
    expect(isRobertOwnedRoute("/unknown")).toBe(false);
  });

  it("treats an exact path as active", () => {
    expect(isRouteActive("/alerts", "/alerts")).toBe(true);
  });

  it("treats a nested route as active", () => {
    expect(isRouteActive("/alerts/123", "/alerts")).toBe(true);
  });

  it("does not treat a similarly prefixed sibling route as active", () => {
    expect(isRouteActive("/alerts-archive", "/alerts")).toBe(false);
    expect(isRouteActive("/dashboard2", "/dashboard")).toBe(false);
  });

  it("does not treat an unrelated path as active", () => {
    expect(isRouteActive("/login", "/alerts")).toBe(false);
  });
});
