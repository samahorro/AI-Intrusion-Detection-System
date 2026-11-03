/**
 * In-memory notification channel for authenticated API requests that receive
 * an explicit HTTP 401. No passwords, tokens or account data are broadcast.
 * An outage (network error / 5xx) must never invalidate a user session.
 */
type ExpiryListener = () => void;
const listeners = new Set<ExpiryListener>();

export function subscribeToSessionExpiry(listener: ExpiryListener): () => void {
  listeners.add(listener);
  return () => { listeners.delete(listener); };
}

export function reportSessionExpiry(): void {
  for (const listener of listeners) listener();
}
