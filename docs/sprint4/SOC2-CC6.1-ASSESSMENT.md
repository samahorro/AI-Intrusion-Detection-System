# Sprint 4 SOC 2 CC6.1 — Logical Access Control Assessment

**Owner:** Robert Gutierrez III  
**Scope:** AEGIS prototype API authentication, sessions, protected resource endpoints, and configuration.  
**Status:** Implementation and automated assessment prepared; not an independent SOC 2 audit or certification.

## Control objective

SOC 2 Trust Services Criteria CC6.1 addresses logical access security: limiting access to software and information assets to authorized users. For this sprint, demonstrate that AEGIS rejects anonymous calls to protected endpoints, validates authenticated sessions, revokes access on logout, records authentication failures, and rejects insecure production session configuration.

## Validation and evidence gathering process

1. Create a feature branch, run `python -m pytest backend/tests/test_soc2_access_control.py -v`, then run the full backend suite and linter.
2. Open a PR to `main`; verify the **Sprint 4 SOC 2 CC6.1 Evidence** workflow has a green check.
3. In GitHub Actions, download the `soc2-cc6.1-evidence-<run-id>` artifact, containing JUnit XML and the human-readable test output.
4. Capture screenshots of the workflow run, test counts, PR review/merge history, and a local session demonstration (unauthorized 401 -> login -> authorized 200 -> logout -> 401). Redact credentials, session cookies, and secrets.
5. Include screenshots, artifact, PR link, commit SHA, assessor name, assessment date, exceptions, and remediation status in the Sprint 4 report. Store evidence in your group's approved location with restricted access.
6. Repeat after any remediation and cite the new run ID. Do not assert a control passed based only on CI if a manual validation failed.

## Test-to-requirement traceability

| Requirement | Automated test | Expected result |
| --- | --- | --- |
| Deny anonymous requests | `test_anonymous_users_cannot_access_protected_resources` | HTTP 401 on protected routes |
| Validate current session | `test_authenticated_user_can_view_own_identity` | HTTP 200 with correct user |
| Terminate access on logout | `test_logout_revokes_access` | HTTP 401 after logout |
| Record failed login attempts | `test_failed_authentication_is_auditable` | Failure row with reason, no password |
| Require a production session secret | `test_production_rejects_insecure_secret` | Insecure startup blocked |
| Require HTTPS frontend in production | `test_production_rejects_plaintext_frontend_origin` | Insecure startup blocked |
| Restrict cross-origin API access | `test_production_secure_headers_and_restricted_origins` | Only configured origin allowed |

## Assessor decision

- **Pass:** all listed tests pass in the PR workflow; reproducible run and manual session evidence are attached.
- **Partial:** tests pass but manual demonstration or evidence is missing.
- **Fail:** any protected route bypasses authentication, session termination fails, or production configuration is insecure.

## Known limitations and follow-up risks

- There is no role-based authorization/least-privilege model; any authenticated account may access endpoints requiring only authentication.
- Self-registration is enabled; approval-based user provisioning is not implemented.
- Login event records support auditability but do not have proven tamper resistance, long-term retention policy, or access-controlled reviewer exports.
- `APP_ENV=production` requires a secret and HTTPS frontend origin, but HTTPS termination, real deployment settings, secret rotation, and secure cookie behavior still need live deployment validation.
- CORS is not an authorization mechanism. API authentication must remain enforced independently.
- This is evidence toward one selected control, not a claim of full CC6.1 compliance or a SOC 2 attestation.
