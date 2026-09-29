import { MockAuthService } from "./MockAuthService";
import { BrowserSessionStore } from "./sessionStore";

const sessionStore = new BrowserSessionStore();

export const authService =
  new MockAuthService(sessionStore);

export { AuthServiceError } from "./AuthServiceError";

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

export {
  MockAuthService,
} from "./MockAuthService";
