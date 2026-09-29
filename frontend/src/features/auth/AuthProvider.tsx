import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type PropsWithChildren,
} from "react";

import type {
  AuthCredentials,
  AuthSession,
  AuthState,
} from "../../types";

import {
  authService as defaultAuthService,
  type AuthService,
} from "../../services/auth";

import {
  AuthContext,
  type AuthContextValue,
} from "./authContext";

export type AuthProviderProps =
  PropsWithChildren<{
    service?: AuthService;
  }>;

export function AuthProvider({
  children,
  service = defaultAuthService,
}: AuthProviderProps) {
  const [state, setState] = useState<AuthState>({
    status: "loading",
  });

  useEffect(() => {
    let cancelled = false;

    async function initializeSession() {
      try {
        const session =
          await service.getCurrentSession();

        if (cancelled) {
          return;
        }

        if (session) {
          setState({
            status: "authenticated",
            session,
          });

          return;
        }

        setState({
          status: "anonymous",
        });
      } catch {
        if (!cancelled) {
          setState({
            status: "anonymous",
          });
        }
      }
    }

    void initializeSession();

    return () => {
      cancelled = true;
    };
  }, [service]);

  const refreshSession =
    useCallback(async (): Promise<void> => {
      setState({
        status: "loading",
      });

      try {
        const session =
          await service.getCurrentSession();

        if (session) {
          setState({
            status: "authenticated",
            session,
          });

          return;
        }

        setState({
          status: "anonymous",
        });
      } catch {
        setState({
          status: "anonymous",
        });
      }
    }, [service]);

  const login = useCallback(
    async (
      credentials: AuthCredentials,
    ): Promise<AuthSession> => {
      setState({
        status: "loading",
      });

      try {
        const session =
          await service.login(credentials);

        setState({
          status: "authenticated",
          session,
        });

        return session;
      } catch (error) {
        setState({
          status: "anonymous",
        });

        throw error;
      }
    },
    [service],
  );

  const logout =
    useCallback(async (): Promise<void> => {
      setState({
        status: "loading",
      });

      try {
        await service.logout();
      } finally {
        setState({
          status: "anonymous",
        });
      }
    }, [service]);

  const value = useMemo<AuthContextValue>(
    () => ({
      state,
      login,
      logout,
      refreshSession,
    }),
    [
      state,
      login,
      logout,
      refreshSession,
    ],
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
