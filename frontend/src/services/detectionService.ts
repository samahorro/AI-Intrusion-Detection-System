import { ApiClient } from "./apiClient";

import type {
  DetectionRequest,
  DetectionResponse,
} from "../types/detection";

export class DetectionService {
  private readonly apiClient: ApiClient;

  constructor(apiClient: ApiClient) {
    this.apiClient = apiClient;
  }

  async analyze(
    request: DetectionRequest,
  ): Promise<DetectionResponse> {
    const response =
      await this.apiClient.post<DetectionResponse>(
        "/detection/analyze",
        request,
      );

    return response.data;
  }
}