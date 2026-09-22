import {
  appRouteRegistry,
  type AppRouteDefinition,
  type FrontendOwner,
} from "./routeRegistry";

export function getRouteByPath(
  path: string,
): AppRouteDefinition | undefined {
  return appRouteRegistry.find(
    (route) => route.path === path,
  );
}

export function getRoutesByOwner(
  owner: FrontendOwner,
): AppRouteDefinition[] {
  return appRouteRegistry.filter(
    (route) => route.owner === owner,
  );
}

export function getPrimaryNavigationRoutes():
  AppRouteDefinition[] {
  return appRouteRegistry.filter(
    (route) => route.showInPrimaryNavigation,
  );
}

export function getProtectedRoutes():
  AppRouteDefinition[] {
  return appRouteRegistry.filter(
    (route) => route.requiresAuth,
  );
}

export function isMonitoringRoute(
  path: string,
): boolean {
  const route = getRouteByPath(path);

  return route?.area === "monitoring";
}

export function isRobertOwnedRoute(
  path: string,
): boolean {
  const route = getRouteByPath(path);

  return route?.owner === "robert";
}

export function isRouteActive(
  currentPath: string,
  routePath: string,
): boolean {
  return (
    currentPath === routePath ||
    currentPath.startsWith(`${routePath}/`)
  );
}
