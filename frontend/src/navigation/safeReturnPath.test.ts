import { describe, expect, it } from "vitest";
import { safeReturnPath } from "./safeReturnPath";

describe("safeReturnPath", () => {
  it("returns to implemented protected routes", () => {
    expect(safeReturnPath("/account")).toBe("/account");
    expect(safeReturnPath("/dashboard?tab=traffic")).toBe("/dashboard");
    expect(safeReturnPath("/alerts")).toBe("/alerts");
  });

  it("rejects external, unimplemented, and public paths", () => {
    for (const from of [
      undefined, null, 123, "https://example.com", "//evil.test",
      "/\\evil.test", "/login", "/admin/users", "/unknown",
    ]) {
      expect(safeReturnPath(from)).toBe("/console");
    }
  });
});
