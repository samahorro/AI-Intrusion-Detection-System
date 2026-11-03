import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type PropsWithChildren,
} from "react";

import type { AuthCredentials, AuthSession, AuthState } from "../../types";
import {
  authService as defaultAuthService,
  type AuthService,
} from "../../services/auth";
import { subscribeToSessionExpiry } from "../../services/auth/sessionExpiryEvents";
import { AuthContext, type AuthContextValue } from "./authContext";

export type AuthProviderProps = PropsWithChildren<{ service?: AuthService }>;

export function AuthProvider({ children, service = defaultAuthService }: AuthProviderProps) {
  const [state, setState] = useState<AuthState>({ status: "loading" });
  // A late response from an older request must not re-authenticate an
  // expired session or overwrite a successful retry/login.
  const requestVersion = useRef(0);
  const verifiedSession = useRef<AuthSession | null>(null);

  useEffect(() => {
    let active = true;
    const version = ++requestVersion.current;

    void service.getCurrentSession().then(
      (session) => {
        if (active && version === requestVersion.current) {
          verifiedSession.current = session;
          setState(session
            ? { status: "authenticated", session }
            : { status: "anonymous" });
        }
      },
      () => {
        // An unavailable backend is not evidence of an invalid session.
        if (active && version === requestVersion.current) {
          setState({ status: "unavailable" });
        }
      },
    );

    return () => { active = false; };
  }, [service]);

  useEffect(() => subscribeToSessionExpiry(() => {
    // A known session also needs revocation while an explicit refresh is in
    // flight. Ignore 401s while signing in or before session verification.
    if (!verifiedSession.current) return;
    verifiedSession.current = null;
    ++requestVersion.current;
    setState({ status: "anonymous", reason: "expired" });
  }), []);

  const refreshSession = useCallback(async (): Promise<void> => {
    const version = ++requestVersion.current;
    setState({ status: "loading" });
    try {
      const session = await service.getCurrentSession();
      if (version === requestVersion.current) {
        verifiedSession.current = session;
        setState(session
          ? { status: "authenticated", session }
          : { status: "anonymous" });
      }
    } catch {
      if (version === requestVersion.current) {
        setState({ status: "unavailable" });
      }
    }
  }, [service]);

  const login = useCallback(async (credentials: AuthCredentials): Promise<AuthSession> => {
    const version = ++requestVersion.current;
    setState({ status: "loading" });
    try {
      const session = await service.login(credentials);
      if (version === requestVersion.current) {
        verifiedSession.current = session;
        setState({ status: "authenticated", session });
      }
      return session;
    } catch (error) {
      if (version === requestVersion.current) {
        verifiedSession.current = null;
        setState({ status: "anonymous" });
      }
      throw error;
    }
  }, [service]);

  const logout = useCallback(async (): Promise<void> => {
    const version = ++requestVersion.current;
    const previousSession = verifiedSession.current;
    // Keep the current view mounted until the server confirms sign-out, so
    // callers can display a retryable error if the logout request fails.
    try {
      await service.logout();
      if (version === requestVersion.current) {
        verifiedSession.current = null;
        setState({ status: "anonymous" });
      }
    } catch (error) {
      // Never claim sign-out succeeded if the server did not confirm it.
      // The cookie may still be valid, so let the user retry.
      if (version === requestVersion.current) {
        setState(previousSession
          ? { status: "authenticated", session: previousSession }
          : { status: "unavailable" });
      }
      throw error;
    }
  }, [service]);

  const value = useMemo<AuthContextValue>(() => ({
    state,
    login,
    logout,
    refreshSession,
  }), [state, login, logout, refreshSession]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
