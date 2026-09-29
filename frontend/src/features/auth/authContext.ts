import { createContext } from "react";

import type {
  AuthCredentials,
  AuthSession,
  AuthState,
} from "../../types";

export type AuthContextValue = {
  state: AuthState;

  login(
    credentials: AuthCredentials,
  ): Promise<AuthSession>;

  logout(): Promise<void>;

  refreshSession(): Promise<void>;
};

export const AuthContext =
  createContext<AuthContextValue | null>(null);
