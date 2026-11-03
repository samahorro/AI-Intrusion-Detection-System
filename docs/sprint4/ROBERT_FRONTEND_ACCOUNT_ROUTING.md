# Sprint 4 — Robert: Account Page and Shared Routing

## Scope (not SOC 2)
This change implements the incomplete frontend work identified in the October 31 AEGIS repository snapshot. It does not alter Kevin's monitoring algorithms, charts, or backend capture endpoints.

### Jira-ready items

**S4-FE-01 — Implement authenticated account/profile page (5 story points)**
- Add read-only `/account` page with the username, ID, and creation date returned by `/auth/me`.
- Reuse the existing AuthProvider session, show sensible fallbacks for missing dates, and require authentication.
- Add tests for authenticated and anonymous behavior.

**S4-FE-02 — Integrate centralized route registry and application shell (3 story points)**
- Make App.tsx derive page paths and authentication requirements from the existing registry.
- Use existing AppShell on standard pages and preserve the custom standalone `/console` layout.
- Enable `/console` and `/account` in navigation, hide `/admin/users` until implementation, and provide a protected 404.
- Use client-side navigation and regression tests.

**S4-BUG-01 — Replace hardcoded console profile username (1 story point)**
- Render the current authenticated username instead of `demo_user`.
- Link the profile dropdown to `/account` and test it.

## Files with important integration considerations
- `frontend/src/App.tsx`: route wiring, protected routing, shared layout.
- `frontend/src/navigation/routeRegistry.ts`: supported route definitions.
- `frontend/src/pages/Account.tsx` and `.css`: new read-only page.
- `frontend/src/services/auth/BackendAuthService.ts`: maps the existing `created_at` field to `createdAt`.
- `frontend/src/components/ProfileMenu.tsx`: reads username from AuthProvider.
- `frontend/src/layouts/AppShell.tsx`: uses React Router links to avoid full reloads.

## Local validation on your Mac
From the repository root:

```bash
cd frontend
npm ci
npm run test
npm run lint
npm run build
```

Backend changes are not part of this patch. No new API endpoint is required. If the backend doesn't return `created_at`, the page displays `Not available`.

## Demo and evidence to capture
1. Sign in and open the Security Console. Show the real username instead of `demo_user`.
2. Open the profile dropdown and select **View account**. Show the authenticated account name, ID, and creation date.
3. Sign out and open `/account` directly. Confirm the protected route redirects to sign-in.
4. Capture passing frontend tests, lint/build, PR review, and CI status.

## Out of scope
- Account editing, password changes, and user administration are not implemented because their backend and permission contracts are not established.
- Changes to Kevin's monitoring dashboard and alert presentation are intentionally avoided.
- A dedicated CC8.1 change-management assessment remains a separate Sprint 4 deliverable.

## Landmark integration
The existing Dashboard and Alerts pages already render their own `<main>` landmarks. The integrated AppShell uses `contentTag="div"` to avoid nested main landmarks, while `/account` and the not-found page supply their own landmarks.
