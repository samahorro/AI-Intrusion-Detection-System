# Application Shell and Route Boundary

## Purpose

This frontend foundation defines the shared application shell and the
ownership boundary between general application infrastructure and
monitoring-specific features.

## Robert-owned responsibilities

The general frontend infrastructure includes:

- application shell
- shared layout
- navigation structure
- authentication route metadata
- account route metadata
- administration route metadata
- reusable page containers
- general section headers
- route ownership definitions

## Kevin-owned monitoring routes

The route registry includes Dashboard and Alerts so the shared shell knows
where monitoring features enter the application.

Their inclusion in the registry does not transfer production ownership.

Kevin remains responsible for the internal implementation of:

- Dashboard
- Alerts
- live monitoring
- threat presentation
- monitoring-specific components
- monitoring data behavior
- WebSocket behavior

## Route metadata

The route registry records:

- route path
- display label
- feature owner
- feature area
- authentication requirement
- primary-navigation visibility

Authentication requirements are metadata only at this stage.

They do not provide security enforcement.

## Security boundary

A route marked requiresAuth does not itself enforce authorization.

Backend services remain authoritative for protected operations.

Actual session-aware and protected-route behavior will be implemented as part
of the authentication/account frontend work.

## Router integration

AppShell is intentionally router-agnostic.

It accepts the current path from the eventual routing layer and renders the
navigation structure without requiring this foundation PR to modify an
existing teammate-owned router.

A later integration change can connect the shell to the project's selected
routing implementation with a small, explicit, peer-reviewed change.

## Handoff model

The intended frontend flow is:

Authentication
-> shared application shell
-> Robert-owned account or administration routes
-> Kevin-owned Dashboard or Alerts routes

This allows both frontend contributors to share application infrastructure
without duplicating production feature ownership.
