import { ApiClient } from "../apiClient";
import { FetchTransport } from "../fetchTransport";

import { BackendAuthService } from "./BackendAuthService";
import { MockAuthService } from "./MockAuthService";
import { BrowserSessionStore } from "./sessionStore";

const sessionStore = new BrowserSessionStore();

const apiBaseUrl = (
  import.meta.env.VITE_API_BASE_URL ??
  "http://localhost:8000"
).replace(/\/$/, "");

const backendAuthService =
  new BackendAuthService(
    new ApiClient(
      new FetchTransport({
        baseUrl: apiBaseUrl,
      }),
    ),
  );

export const authService =
  import.meta.env.VITE_USE_MOCK_AUTH === "true"
    ? new MockAuthService(sessionStore)
    : backendAuthService;

export { AuthServiceError } from "./AuthServiceError";
export { BackendAuthService } from "./BackendAuthService";
export { MockAuthService } from "./MockAuthService";

export type {
  AuthErrorCode,
} from "./AuthServiceError";

export type {
  AuthService,
} from "./authService";

export {
  BrowserSessionStore,
} from "./sessionStore";

export type {
  SessionStore,
} from "./sessionStore";
