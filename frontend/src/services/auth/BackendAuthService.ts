import {
  ApiClientError,
  type ApiClient,
} from "../apiClient";

import type {
  AuthCredentials,
  AuthSession,
  AuthenticatedUser,
} from "../../types";

import type { AuthService } from "./authService";
import { AuthServiceError } from "./AuthServiceError";

type BackendUser = {
  id: number | string;
  username: string;
  created_at?: string | null;
};

type LoginResponse = {
  message: string;
  user: BackendUser;
};

type CurrentUserResponse = {
  user: BackendUser;
};

function mapBackendUser(
  user: BackendUser,
): AuthenticatedUser {
  return {
    id: String(user.id),
    username: user.username,
    displayName: user.username,
    role: "user",
    permissions: [],
  };
}

function mapServiceError(
  error: unknown,
  invalidCredentialsOnUnauthorized = false,
): AuthServiceError {
  if (error instanceof AuthServiceError) {
    return error;
  }

  if (error instanceof ApiClientError) {
    if (
      invalidCredentialsOnUnauthorized &&
      error.status === 401
    ) {
      return new AuthServiceError(
        "INVALID_CREDENTIALS",
        "The username or password is incorrect.",
      );
    }

    return new AuthServiceError(
      "UNKNOWN_ERROR",
      error.message,
    );
  }

  if (error instanceof TypeError) {
    return new AuthServiceError(
      "NETWORK_ERROR",
      "Unable to reach the authentication service.",
    );
  }

  return new AuthServiceError(
    "UNKNOWN_ERROR",
    "Authentication request failed.",
  );
}

export class BackendAuthService implements AuthService {
  private readonly client: ApiClient;

  constructor(client: ApiClient) {
    this.client = client;
  }

  async login(
    credentials: AuthCredentials,
  ): Promise<AuthSession> {
    try {
      const response =
        await this.client.post<LoginResponse>(
          "/auth/login",
          {
            username: credentials.username.trim(),
            password: credentials.password,
          },
        );

      return {
        user: mapBackendUser(response.data.user),
      };
    } catch (error) {
      throw mapServiceError(error, true);
    }
  }

  async logout(): Promise<void> {
    try {
      await this.client.post(
        "/auth/logout",
      );
    } catch (error) {
      throw mapServiceError(error);
    }
  }

  async getCurrentSession():
    Promise<AuthSession | null> {
    try {
      const response =
        await this.client.get<CurrentUserResponse>(
          "/auth/me",
        );

      return {
        user: mapBackendUser(response.data.user),
      };
    } catch (error) {
      if (
        error instanceof ApiClientError &&
        error.status === 401
      ) {
        return null;
      }

      throw mapServiceError(error);
    }
  }
}
