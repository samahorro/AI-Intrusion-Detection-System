import { describe, expect, it } from "vitest";
import { resolveApiBaseUrl } from "./apiBaseUrl";

describe("shared API base URL resolution", () => {
  it("uses the canonical URL when both environment settings are present", () => {
    expect(resolveApiBaseUrl("https://api.example.test/v1/", "http://localhost:8000"))
      .toBe("https://api.example.test/v1");
  });

  it("supports the existing VITE_API_BASE_URL setting for all services", () => {
    expect(resolveApiBaseUrl(undefined, "https://backend.example.test/"))
      .toBe("https://backend.example.test");
  });

  it("ignores empty configuration and removes trailing slashes", () => {
    expect(resolveApiBaseUrl("   ", " https://demo.example.test/// "))
      .toBe("https://demo.example.test");
  });

  it("defaults to the local backend when neither value is configured", () => {
    expect(resolveApiBaseUrl()).toBe("http://localhost:8000");
  });
});
