import type {
  AuthCredentials,
  AuthSession,
} from "../../types";

export interface AuthService {
  login(
    credentials: AuthCredentials,
  ): Promise<AuthSession>;

  logout(): Promise<void>;

  getCurrentSession():
    Promise<AuthSession | null>;
}
