import type { AuthSession } from "../../types";

const SESSION_STORAGE_KEY = "ai-ids.auth.session";

export interface SessionStore {
  read(): AuthSession | null;
  write(session: AuthSession): void;
  clear(): void;
}

function isAuthSession(value: unknown): value is AuthSession {
  if (!value || typeof value !== "object") {
    return false;
  }

  const session = value as Partial<AuthSession>;

  return (
    typeof session.accessToken === "string" &&
    typeof session.expiresAt === "string" &&
    Boolean(session.user) &&
    typeof session.user?.id === "string" &&
    typeof session.user?.email === "string"
  );
}

export class BrowserSessionStore implements SessionStore {
  read(): AuthSession | null {
    if (typeof window === "undefined") {
      return null;
    }

    const storedValue =
      window.sessionStorage.getItem(SESSION_STORAGE_KEY);

    if (!storedValue) {
      return null;
    }

    try {
      const parsed: unknown = JSON.parse(storedValue);

      if (!isAuthSession(parsed)) {
        this.clear();
        return null;
      }

      const expiration =
        new Date(parsed.expiresAt).getTime();

      if (
        Number.isNaN(expiration) ||
        expiration <= Date.now()
      ) {
        this.clear();
        return null;
      }

      return parsed;
    } catch {
      this.clear();
      return null;
    }
  }

  write(session: AuthSession): void {
    if (typeof window === "undefined") {
      return;
    }

    window.sessionStorage.setItem(
      SESSION_STORAGE_KEY,
      JSON.stringify(session),
    );
  }

  clear(): void {
    if (typeof window === "undefined") {
      return;
    }

    window.sessionStorage.removeItem(
      SESSION_STORAGE_KEY,
    );
  }
}
