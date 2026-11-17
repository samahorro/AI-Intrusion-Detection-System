import { ApiClient } from "../apiClient";
import { resolveApiBaseUrl } from "../apiBaseUrl";
import { FetchTransport } from "../fetchTransport";

import { BackendAuthService } from "./BackendAuthService";
import { MockAuthService } from "./MockAuthService";
import { BrowserSessionStore } from "./sessionStore";

const sessionStore = new BrowserSessionStore();

const apiBaseUrl = resolveApiBaseUrl(
  import.meta.env.VITE_API_URL,
  import.meta.env.VITE_API_BASE_URL,
);

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
