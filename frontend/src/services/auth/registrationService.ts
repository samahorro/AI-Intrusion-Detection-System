import {
  ApiClient,
  ApiClientError,
} from "../apiClient";
import { resolveApiBaseUrl } from "../apiBaseUrl";
import { FetchTransport } from "../fetchTransport";

export type RegisterCredentials = {
  username: string;
  password: string;
};

export type RegisteredUser = {
  id: number | string;
  username: string;
  created_at?: string | null;
};

type RegisterResponse = {
  message: string;
  user: RegisteredUser;
};

const apiBaseUrl = resolveApiBaseUrl(
  import.meta.env.VITE_API_URL,
  import.meta.env.VITE_API_BASE_URL,
);

const client = new ApiClient(
  new FetchTransport({
    baseUrl: apiBaseUrl,
  }),
);

export async function registerUser(
  credentials: RegisterCredentials,
): Promise<RegisterResponse> {
  try {
    const response =
      await client.post<RegisterResponse>(
        "/auth/register",
        {
          username: credentials.username.trim(),
          password: credentials.password,
        },
      );

    return response.data;
  } catch (error) {
    if (error instanceof ApiClientError) {
      throw new Error(error.message);
    }

    if (error instanceof TypeError) {
      throw new Error(
        "Unable to reach the registration service.",
      );
    }

    throw new Error(
      "Unable to create account.",
    );
  }
}