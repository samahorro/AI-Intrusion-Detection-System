# Robert-Owned Frontend Foundation

This directory and the related base components, state components,
types, and service layer establish shared frontend infrastructure for
Robert Gutierrez III's assigned CPSC 491 scope.

## Included in this foundation

- Reusable Button component
- Reusable Input component
- Form-field structure
- Reusable Card component
- General-purpose Modal component
- Loading state
- Empty state
- Error state
- Generic API request/response types
- Authentication/session type foundations
- User-administration type foundations
- API client abstraction
- Fetch-based transport
- Mock transport for development before backend endpoints are ready

## Ownership boundary

This foundation is intended for general application infrastructure,
authentication/account interfaces, and user-administration interfaces.

It does not implement:

- Dashboard functionality
- Alerts functionality
- Live monitoring
- Threat presentation
- WebSocket monitoring behavior
- Monitoring-specific components

Those feature areas remain separate from this infrastructure.

## Security boundary

Frontend roles, permissions, account states, and UI visibility are
representations of backend-defined behavior.

Client-side UI behavior must not be treated as authoritative
authorization for protected operations.
