import type {
  ApiRequest,
  ApiResponse,
  HttpMethod,
} from "../types";

import type { ApiTransport } from "./apiClient";

export type MockHandler = (
  request: ApiRequest,
) =>
  | ApiResponse<unknown>
  | Promise<ApiResponse<unknown>>;

function createKey(
  method: HttpMethod,
  path: string,
) {
  return `${method} ${path}`;
}

export class MockTransport implements ApiTransport {
  private readonly handlers =
    new Map<string, MockHandler>();

  when(
    method: HttpMethod,
    path: string,
    handler: MockHandler,
  ) {
    this.handlers.set(
      createKey(method, path),
      handler,
    );

    return this;
  }

  async request<T>(
    request: ApiRequest,
  ): Promise<ApiResponse<T>> {
    const handler = this.handlers.get(
      createKey(request.method, request.path),
    );

    if (!handler) {
      throw new Error(
        `No mock handler registered for ${request.method} ${request.path}`,
      );
    }

    const response = await handler(request);

    return response as ApiResponse<T>;
  }
}
