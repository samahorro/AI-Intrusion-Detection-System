import type {
  AuthState,
  AuthenticatedUser,
} from "../../types";

export function isAuthenticated(
  state: AuthState,
): boolean {
  return state.status === "authenticated";
}

export function isAuthLoading(
  state: AuthState,
): boolean {
  return state.status === "loading";
}

export function getAuthenticatedUser(
  state: AuthState,
): AuthenticatedUser | null {
  if (state.status !== "authenticated") {
    return null;
  }

  return state.session.user;
}
