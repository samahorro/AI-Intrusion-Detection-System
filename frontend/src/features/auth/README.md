# Authentication and Session Foundation

This feature provides Robert-owned frontend authentication and session infrastructure for the AI Intrusion Detection System.

## Current behavior

Authentication now uses the backend session API by default:

- `POST /auth/login`
- `GET /auth/me`
- `POST /auth/logout`

The browser sends the backend session cookie by using `credentials: "include"` in the shared fetch transport. The frontend does not create or store a fake access token for backend-authenticated sessions.

Set `VITE_API_BASE_URL` when the backend is not running at `http://localhost:8000`.

## Optional mock mode

The mock authentication service remains available for isolated frontend development.

Start Vite with `VITE_USE_MOCK_AUTH=true` to use it.

Mock credentials:

- Username: `demo`
- Password: `demo-password`

Mock sessions are stored in `sessionStorage` and are used only when mock mode is explicitly enabled.

## Session behavior

`AuthProvider` owns the frontend authentication state.

Supported states are:

- loading (session check in progress)
- anonymous (including an explicit expired-session reason)
- unavailable (the authentication service could not be reached or failed)
- authenticated

On startup, the provider checks `/auth/me`. A valid backend cookie session restores the authenticated user. A `401 Unauthorized` from `/auth/me` indicates there is no valid session. A transport error or server outage instead displays a retryable session-check error without claiming the user was logged out.

For authenticated users, a `401` response from a protected API endpoint expires the local authenticated view. Both `captureService` and `FetchTransport` report those responses to the provider; login failures and initial `/auth/me` probes are excluded. Stale session-check responses cannot re-authenticate an expired session. Retrying session verification does not require storing a browser access token.

Protected pages retain their permitted route destination when redirecting to `/login`, so a successful sign-in can return to that route. Unrecognized or external redirect targets are discarded.

Logout requires a successful backend confirmation before the interface claims sign-out succeeded. If the network request fails, the user retains a retryable sign-out action instead of seeing a misleading success state.

## Protected routes

`ProtectedRoute` prevents anonymous users from opening authenticated application routes. Dashboard and Alerts remain Kevin-owned monitoring pages; Robert's route guard only controls the authentication boundary around them.

## Backend contract

The current backend authenticates with `username` and `password`. The frontend login form mirrors the backend username validation rules so invalid values can be rejected before a network request is made.

## Security boundary

Frontend route visibility does not provide authoritative authorization. The backend remains responsible for enforcing protected operations.

Roles and permissions are still placeholder presentation values until Derrick's final security policy and backend contract are available.
