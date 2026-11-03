import { describe, expect, it, vi } from "vitest";
import { reportSessionExpiry, subscribeToSessionExpiry } from "./sessionExpiryEvents";

describe("sessionExpiryEvents", () => {
  it("notifies current listeners and permits unsubscribing", () => {
    const listener = vi.fn();
    const unsubscribe = subscribeToSessionExpiry(listener);
    reportSessionExpiry();
    expect(listener).toHaveBeenCalledTimes(1);
    unsubscribe();
    reportSessionExpiry();
    expect(listener).toHaveBeenCalledTimes(1);
  });
});
