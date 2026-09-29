# Authentication and Session Foundation

This feature provides Robert-owned frontend authentication and
session infrastructure for the AI Intrusion Detection System.

## Current Sprint 2 behavior

Authentication currently uses a mock service so frontend development
can continue before the final backend authentication endpoints are
available.

Development credentials:

- Email: demo@example.com
- Password: demo-password

These credentials exist only for local frontend development.

## Session behavior

Successful mock authentication creates a development session containing:

- access token
- expiration timestamp
- authenticated user information

The session is stored in browser sessionStorage.

Expired, malformed, or missing session data is treated as an anonymous
session.

Logout clears the stored frontend session.

## React integration

AuthProvider owns the current frontend authentication state.

Supported states are:

- loading
- anonymous
- authenticated

Components can access the current state and authentication actions with
the useAuth hook.

## Backend integration

UI components should depend on the AuthService contract rather than
directly implementing HTTP requests.

A future real authentication service can therefore replace
MockAuthService without requiring login/account components to contain
backend request logic.

## Security boundary

Frontend session state and route visibility do not provide authoritative
authorization.

The backend remains responsible for enforcing protected operations.

Roles and permissions in the mock user are placeholders only and must
not be treated as final Derrick-defined security policy.
