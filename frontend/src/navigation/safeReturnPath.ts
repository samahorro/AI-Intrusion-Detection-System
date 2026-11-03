import { getRouteByPath } from "./routeUtils";

/** Allow only implemented, authenticated internal routes after login. */
export function safeReturnPath(candidate: unknown): string {
  if (typeof candidate !== "string" ||
      !candidate.startsWith("/") ||
      candidate.startsWith("//") ||
      candidate.includes("\\")) {
    return "/console";
  }

  const pathname = candidate.split(/[?#]/, 1)[0];
  const route = getRouteByPath(pathname);
  if (!route?.requiresAuth || route.id === "admin-users") {
    return "/console";
  }
  // Don't copy query strings from untrusted navigation state.
  return pathname;
}
