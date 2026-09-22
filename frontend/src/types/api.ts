export type HttpMethod =
  | "GET"
  | "POST"
  | "PUT"
  | "PATCH"
  | "DELETE";

export type ApiRequest = {
  method: HttpMethod;
  path: string;
  headers?: Record<string, string>;
  body?: unknown;
};

export type ApiResponse<T> = {
  status: number;
  data: T;
};

export type ApiErrorPayload = {
  message?: string;
  code?: string;
  details?: unknown;
};
