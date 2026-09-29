import type {
  AuthCredentials,
  AuthSession,
  AuthenticatedUser,
} from "../../types";

import type { AuthService } from "./authService";
import type { SessionStore } from "./sessionStore";

import { AuthServiceError } from "./AuthServiceError";

const MOCK_EMAIL = "demo@example.com";
const MOCK_PASSWORD = "demo-password";

const MOCK_USER: AuthenticatedUser = {
  id: "mock-user-001",
  email: MOCK_EMAIL,
  displayName: "Development User",
  role: "mock-user",
  permissions: [],
};

function wait(milliseconds: number): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, milliseconds);
  });
}

export class MockAuthService implements AuthService {
  private readonly sessionStore: SessionStore;

  constructor(sessionStore: SessionStore) {
    this.sessionStore = sessionStore;
  }

  async login(
    credentials: AuthCredentials,
  ): Promise<AuthSession> {
    await wait(400);

    const normalizedEmail =
      credentials.email.trim().toLowerCase();

    if (
      normalizedEmail !== MOCK_EMAIL ||
      credentials.password !== MOCK_PASSWORD
    ) {
      throw new AuthServiceError(
        "INVALID_CREDENTIALS",
        "The email or password is incorrect.",
      );
    }

    const session: AuthSession = {
      accessToken: "mock-development-access-token",
      expiresAt: new Date(
        Date.now() + 60 * 60 * 1000,
      ).toISOString(),
      user: MOCK_USER,
    };

    this.sessionStore.write(session);

    return session;
  }

  async logout(): Promise<void> {
    await wait(150);
    this.sessionStore.clear();
  }

  async getCurrentSession():
    Promise<AuthSession | null> {
    await wait(150);
    return this.sessionStore.read();
  }
}
