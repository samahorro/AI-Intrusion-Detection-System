# Robert — Sprint 4 Jira tickets (ready to copy)

Use the team's actual Jira issue keys, sprint dates, and statuses. These are proposed tickets, **not created Jira issues**.

## Ticket 1 — Harden production authentication and sessions
**Type:** Story | **Priority:** High | **Owner:** Robert | **Estimate:** 3 points

Implement fail-fast production configuration for secure session keys, HTTPS frontend origin, secure cookies, and HTTP security headers. Preserve existing local-development behavior. Files: `backend/app/main.py`.

**Acceptance criteria:** insecure production boot rejects missing/short session secret or non-HTTPS frontend; secure production responses set security headers; development workflow still works; review confirms no secret is committed.

## Ticket 2 — Automate SOC 2 CC6.1 control tests
**Type:** Story | **Priority:** High | **Owner:** Robert | **Estimate:** 3 points

Build reproducible regression tests for session authorization, anonymous request denial, logout revocation, authentication audit records, and production security configuration. Files: `backend/tests/test_soc2_access_control.py`.

**Acceptance criteria:** access-control suite passes; required paths return 401 without authentication; successful session returns current user; logout invalidates access; invalid login is recorded without secret material.

## Ticket 3 — Publish SOC 2 validation artifacts in GitHub Actions
**Type:** Task | **Priority:** High | **Owner:** Robert | **Estimate:** 2 points

Add a dedicated CI workflow that runs the control tests on PR and main, exports JUnit XML and human-readable test output, and uploads them for grading. Files: `.github/workflows/soc2-access-control.yml`.

**Acceptance criteria:** PR workflow is green, job artifact downloads, run URL and commit SHA attached to Jira, and the artifact is retained for 30 days.

## Ticket 4 — Conduct and document control assessment
**Type:** Task | **Priority:** High | **Owner:** Robert | **Estimate:** 3 points

Independently validate results after merging, capture redacted login/unauthorized/logout/CI screenshots, assess exceptions, and report a defensible pass, partial, or fail outcome. File: `docs/sprint4/SOC2-CC6.1-ASSESSMENT.md`.

**Acceptance criteria:** test matrix populated with actual results; screenshot set and GitHub evidence artifact referenced; manual results agree with CI; unresolved risks and remediation plan are disclosed.

## Ticket 5 — Address remaining access governance gaps (follow-up)
**Type:** Technical debt | **Priority:** Medium | **Owner:** Coordinate with group | **Estimate:** 5 points

Agree on registration/approval requirements and least-privilege roles before exposing the prototype publicly. Do not change shared authentication policy without group review.

**Acceptance criteria:** role matrix, approval model, and dedicated authorization tests proposed; ownership confirmed by group.

## Suggested PR breakdown

- **PR A:** hardening + CC6.1 tests (tickets 1 and 2).
- **PR B:** dedicated CI evidence export + assessment documentation (tickets 3 and 4).
- **Ticket 5:** new future PR only after ownership and requirements are agreed.

## Suggested schedule

- **Nov 1–3, 2026:** create Jira tasks, push PR A, run full Python tests.
- **Nov 4–6, 2026:** review/merge PR A; push PR B; export CI evidence.
- **Nov 7–8, 2026:** complete draft assessment and screenshot set.
- **Following week:** final assessment, remediation and submission according to the professor's official deadlines.
