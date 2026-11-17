/**
 * Use one backend origin for login, capture, and other frontend API calls.
 * VITE_API_URL is the canonical setting; VITE_API_BASE_URL is supported for
 * existing local configurations.
 */
export function resolveApiBaseUrl(
  apiUrl?: string,
  legacyBaseUrl?: string,
): string {
  const configuredUrl = apiUrl?.trim() || legacyBaseUrl?.trim();
  return (configuredUrl || "http://localhost:8000").replace(/\/+$/, "");
}
