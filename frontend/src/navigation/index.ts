export {
  appRouteRegistry,
} from "./routeRegistry";

export type {
  AppRouteDefinition,
  FrontendOwner,
  RouteArea,
} from "./routeRegistry";

export {
  getPrimaryNavigationRoutes,
  getProtectedRoutes,
  getRouteByPath,
  getRoutesByOwner,
  isMonitoringRoute,
  isRobertOwnedRoute,
  isRouteActive,
} from "./routeUtils";
