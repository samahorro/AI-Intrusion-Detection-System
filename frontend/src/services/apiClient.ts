import type {
  ApiErrorPayload,
  ApiRequest,
  ApiResponse,
} from "../types";

export interface ApiTransport {
  request<T>(request: ApiRequest): Promise<ApiResponse<T>>;
}

export class ApiClientError extends Error {
  readonly status: number;
  readonly code?: string;
  readonly details?: unknown;

  constructor(
    status: number,
    payload: ApiErrorPayload = {},
  ) {
    super(payload.message ?? `Request failed with status ${status}`);

    this.name = "ApiClientError";
    this.status = status;
    this.code = payload.code;
    this.details = payload.details;
  }
}

export class ApiClient {
  constructor(private readonly transport: ApiTransport) {}

  get<T>(
    path: string,
    headers?: Record<string, string>,
  ) {
    return this.transport.request<T>({
      method: "GET",
      path,
      headers,
    });
  }

  post<T>(
    path: string,
    body?: unknown,
    headers?: Record<string, string>,
  ) {
    return this.transport.request<T>({
      method: "POST",
      path,
      body,
      headers,
    });
  }

  put<T>(
    path: string,
    body?: unknown,
    headers?: Record<string, string>,
  ) {
    return this.transport.request<T>({
      method: "PUT",
      path,
      body,
      headers,
    });
  }

  patch<T>(
    path: string,
    body?: unknown,
    headers?: Record<string, string>,
  ) {
    return this.transport.request<T>({
      method: "PATCH",
      path,
      body,
      headers,
    });
  }

  delete<T>(
    path: string,
    headers?: Record<string, string>,
  ) {
    return this.transport.request<T>({
      method: "DELETE",
      path,
      headers,
    });
  }
}
