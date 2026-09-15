# Frontend Architecture and Ownership

## Purpose

This document defines the frontend ownership boundaries and integration strategy
for the AI Intrusion Detection System project.

The goal is to allow multiple frontend contributors to work in parallel without
duplicating production features or creating conflicting implementations.

## Robert Gutierrez III - Frontend Ownership

Robert owns the general frontend infrastructure and the user-facing flows that
surround the monitoring experience.

Primary responsibilities:

- General application shell and shared layout
- Routing infrastructure
- Authentication interfaces
- Account and profile interfaces
- User-administration interfaces
- Base reusable frontend components
- Frontend API/service patterns for owned features
- Loading, empty, success, validation, and error-state patterns
- Accessibility and regression testing for owned frontend flows
- Integration boundary between authenticated application structure and
  monitoring routes

Examples of reusable base components that may be owned by Robert include:

- Button
- Input
- Form controls
- Card
- Modal/Dialog
- Layout wrappers
- Generic loading states
- Generic empty states
- Generic error states

## Kevin Chang - Monitoring Frontend Ownership

Kevin owns the monitoring-specific frontend experience.

Primary responsibilities include:

- Dashboard
- Alerts
- Live monitoring
- Threat presentation
- Threat details
- Response interaction
- IDS/system status presentation
- WebSocket/live-update behavior
- Monitoring-specific components

Examples of monitoring-specific components include:

- ThreatBadge
- StatusBadge
- AlertCard
- SystemStatusCard
- DeviceTable
- ThreatCounter
- RecentAlerts
- ScanControl
- ConnectionStatus
- ThreatDetails

Robert should not create duplicate production implementations of these
monitoring features.

## Derrick - Security Boundary

Derrick defines security and user-administration rules, including:

- Roles
- Permissions
- Account states
- Authorization behavior
- Security constraints

The frontend may represent these rules in the interface, but client-side UI
behavior is not considered authoritative authorization.

Protected operations must remain enforced by the backend.

## Samantha - Backend/API Boundary

Samantha owns backend/API/database services consumed by the frontend.

Robert will consume backend contracts for:

- Authentication
- Account/profile functionality
- User administration
- Shared application state

API logic should be centralized in a frontend service layer instead of being
spread directly throughout React components.

## Route Integration Strategy

The shared frontend should provide a stable application shell and route
structure.

Robert-owned routes may include:

- /login
- /account
- /profile
- /settings
- /admin/users

Kevin-owned monitoring routes may include:

- /dashboard
- /alerts

The shared routing layer should allow Kevin-owned monitoring pages to plug into
the application without Robert recreating their internal monitoring logic.

## Temporary Placeholders

A temporary placeholder may be created only when necessary to unblock routing
or integration work.

A placeholder:

- is not considered final feature ownership
- should not duplicate another contributor's production implementation
- should be replaced by the owning contributor's real feature

## Cross-Owner Changes

Changes to another contributor's owned feature area should be:

1. Limited to the minimum integration change necessary.
2. Clearly identified in the Jira issue.
3. Clearly described in the pull request.
4. Reviewed by the appropriate feature owner.

## GitHub Workflow

Frontend work should follow this workflow:

1. Start from the current shared main branch.
2. Create a feature-specific branch.
3. Implement one reviewable unit of work.
4. Run applicable tests and checks.
5. Review the Git diff before committing.
6. Commit using a descriptive message.
7. Push the branch to GitHub.
8. Open a pull request into main.
9. Request peer review.
10. Merge only after review.

## Pull Request Scope Rule

Pull requests should make ownership clear.

A Robert-owned frontend PR should avoid modifying Dashboard, Alerts, live
monitoring, monitoring components, monitoring mock data, or WebSocket behavior
unless the PR is explicitly identified as cross-owner integration support.

## Current Architecture Goal

The intended frontend flow is:

Authentication
-> Shared application shell/navigation
-> Account/profile or administration functionality
-> Monitoring route handoff
-> Kevin-owned Dashboard/Alerts experience

This structure preserves individual ownership while still producing one
integrated frontend application.
