import {
  ApiClientError,
  type ApiTransport,
} from "./apiClient";

import type {
  ApiErrorPayload,
  ApiRequest,
  ApiResponse,
} from "../types";

export type FetchTransportOptions = {
  baseUrl: string;
  getAccessToken?: () => string | null;
};

export class FetchTransport implements ApiTransport {
  constructor(
    private readonly options: FetchTransportOptions,
  ) {}

  async request<T>(
    request: ApiRequest,
  ): Promise<ApiResponse<T>> {
    const token = this.options.getAccessToken?.();

    const headers: Record<string, string> = {
      Accept: "application/json",
      ...request.headers,
    };

    if (request.body !== undefined) {
      headers["Content-Type"] = "application/json";
    }

    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(
      `${this.options.baseUrl}${request.path}`,
      {
        method: request.method,
        headers,
        body:
          request.body === undefined
            ? undefined
            : JSON.stringify(request.body),
      },
    );

    const contentType =
      response.headers.get("content-type") ?? "";

    const hasJson =
      contentType.includes("application/json");

    const data = hasJson
      ? await response.json()
      : null;

    if (!response.ok) {
      const payload: ApiErrorPayload =
        data && typeof data === "object"
          ? (data as ApiErrorPayload)
          : {
              message: `Request failed with status ${response.status}`,
            };

      throw new ApiClientError(
        response.status,
        payload,
      );
    }

    return {
      status: response.status,
      data: data as T,
    };
  }
}
