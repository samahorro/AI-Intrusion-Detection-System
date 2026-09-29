export type AuthErrorCode =
  | "INVALID_CREDENTIALS"
  | "SESSION_EXPIRED"
  | "NETWORK_ERROR"
  | "UNKNOWN_ERROR";

export class AuthServiceError extends Error {
  readonly code: AuthErrorCode;

  constructor(
    code: AuthErrorCode,
    message: string,
  ) {
    super(message);

    this.name = "AuthServiceError";
    this.code = code;
  }
}
