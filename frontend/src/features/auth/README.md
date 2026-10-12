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

- loading
- anonymous
- authenticated

On startup, the provider checks `/auth/me`. A valid backend session restores the authenticated user. A `401 Unauthorized` response is treated as an anonymous session.

Logout calls the backend logout endpoint and returns the frontend to the anonymous state.

## Protected routes

`ProtectedRoute` prevents anonymous users from opening authenticated application routes. Dashboard and Alerts remain Kevin-owned monitoring pages; Robert's route guard only controls the authentication boundary around them.

## Backend contract

The current backend authenticates with `username` and `password`. The frontend login form mirrors the backend username validation rules so invalid values can be rejected before a network request is made.

## Security boundary

Frontend route visibility does not provide authoritative authorization. The backend remains responsible for enforcing protected operations.

Roles and permissions are still placeholder presentation values until Derrick's final security policy and backend contract are available.
