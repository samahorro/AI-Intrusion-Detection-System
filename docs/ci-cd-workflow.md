# CI/CD Workflow and Local Validation Guide

## Purpose

This document describes the continuous integration and validation process used
by the AI Intrusion Detection System project.

The CI/CD pipeline is intended to catch build, test, lint, and integration
failures before changes are merged into the shared `main` branch.

The project currently validates four major areas:

1. Backend
2. Frontend
3. AI/ML
4. Frontend-backend integration

Contributors should run the appropriate local checks before opening a pull
request.

---

## CI Workflow Summary

| Workflow | File | Primary Validation |
|---|---|---|
| Backend CI | `.github/workflows/ci.yml` | Backend imports and automated tests |
| Frontend CI | `.github/workflows/frontend-ci.yml` | Lint, frontend tests, and production build |
| AI/ML CI | `.github/workflows/ml-ci.yml` | AI/ML automated tests |
| Integration CI | `.github/workflows/integration-ci.yml` | Frontend/backend startup and API smoke validation |

---

## Backend CI

The backend workflow is defined in:

` .github/workflows/ci.yml `

It currently:

1. Checks out the repository.
2. Sets up Python.
3. Installs dependencies from `backend/requirements.txt`.
4. Verifies that the backend application imports.
5. Runs the backend automated tests.

### Local Backend Validation

From the repository root:

```bash
python3 -m pip install -r backend/requirements.txt

```

Verify the backend imports:

```bash
python3 -c "from backend.app.main import app; print('Backend import successful')"
```

Run the backend tests:

```bash
python3 -m pytest backend/tests -v
```

The backend test suite currently validates authentication and health behavior.

---

## Frontend CI

The frontend workflow is defined in:

`.github/workflows/frontend-ci.yml`

It currently:

1. Checks out the repository.
2. Sets up Node.js.
3. Installs dependencies with `npm ci`.
4. Runs lint validation.
5. Runs frontend tests.
6. Creates the production build.

### Local Frontend Validation

Enter the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm ci
```

Run lint:

```bash
npm run lint
```

Run frontend tests:

```bash
npm run test
```

Run the production build:

```bash
npm run build
```

Return to the repository root:

```bash
cd ..
```

---

## AI/ML CI

The AI/ML workflow is defined in:

`.github/workflows/ml-ci.yml`

It runs the project's AI/ML automated test suite.

### Local AI/ML Validation

Install pytest if necessary:

```bash
python3 -m pip install pytest
```

Run the ML tests:

```bash
python3 -m pytest ml/tests -v
```
---

## Frontend-Backend Integration CI

The integration workflow is defined in:

`.github/workflows/integration-ci.yml`

The reusable smoke-test script is:

`scripts/ci/frontend_backend_smoke.sh`

The integration smoke test validates that the frontend and backend can operate
together in the CI environment.

It verifies:

1. The frontend production build succeeds.
2. The backend application starts.
3. The frontend preview server starts.
4. The backend `/health` endpoint responds.
5. The frontend root document loads.
6. A temporary user can be registered.
7. The temporary user can log in.
8. The authenticated session can access `/auth/me`.
9. The user can log out successfully.
10. The session can no longer access `/auth/me` after logout.
11. Temporary processes and resources are cleaned up.

### Local Integration Validation

Install backend dependencies:

```bash
python3 -m pip install -r backend/requirements.txt
```

Install frontend dependencies:

```bash
npm ci --prefix frontend
```

Run the smoke test:

```bash
./scripts/ci/frontend_backend_smoke.sh
```

A successful run ends with:

```text
Frontend-backend smoke test passed.
```
---

## Recommended Validation Before a Pull Request

Contributors should run the checks that correspond to the area they changed.

### Frontend Changes

From `frontend/`:

```bash
npm run lint
npm run test
npm run build
```

### Backend Changes

From the repository root:

```bash
python3 -c "from backend.app.main import app; print('Backend import successful')"
python3 -m pytest backend/tests -v
```

### AI/ML Changes

From the repository root:

```bash
python3 -m pytest ml/tests -v
```

### Cross-Stack Changes

From the repository root:

```bash
./scripts/ci/frontend_backend_smoke.sh
```

For changes that affect more than one subsystem, contributors should also run
the individual checks for those areas when practical.

---

## Reproducing CI Failures Locally

When a GitHub Actions job fails, first identify which workflow failed.

### Frontend Failure

```bash
cd frontend
npm ci
npm run lint
npm run test
npm run build
```

### Backend Failure

```bash
python3 -m pip install -r backend/requirements.txt
python3 -c "from backend.app.main import app; print('Backend import successful')"
python3 -m pytest backend/tests -v
```

### AI/ML Failure

```bash
python3 -m pip install pytest
python3 -m pytest ml/tests -v
```

### Integration Failure

```bash
./scripts/ci/frontend_backend_smoke.sh
```

If the integration test cannot connect to the backend, verify that backend
dependencies are installed and that port `8000` is available.

If the frontend preview cannot start, verify that frontend dependencies are
installed and that port `4173` is available.

---

## Python Command Note

GitHub Actions configures Python automatically.

On macOS development environments, the executable is commonly named:

```text
python3
```

For this reason, the project's local CI/CD commands and integration smoke-test
script use `python3`.

---

## Pull Request Expectations

Before submitting a pull request:

1. Update the local repository from `main`.
2. Create a feature-specific branch.
3. Keep the pull request focused on one change.
4. Run the appropriate local validation.
5. Review the Git diff.
6. Commit with a descriptive message.
7. Push the branch.
8. Open a pull request targeting `main`.
9. Reference the appropriate Jira issue.
10. Request peer review.
11. Merge after required review and CI validation succeed.

CI validation does not replace peer review. Both automated checks and human
review are part of the project workflow.

---

## CI/CD Responsibility Boundaries

CI/CD validation may exercise code owned by multiple contributors without
changing ownership of that production code.

For example, the frontend-backend integration smoke test validates both
subsystems without transferring ownership of frontend or backend production
features.

Cross-owner production changes should still be limited, documented, and
reviewed by the appropriate contributor.

---

## Current Validation Flow

```text
Pull Request
     |
     +--> Backend CI
     |      |
     |      +--> Import Validation
     |      +--> Backend Tests
     |
     +--> Frontend CI
     |      |
     |      +--> Lint
     |      +--> Frontend Tests
     |      +--> Production Build
     |
     +--> AI/ML CI
     |      |
     |      +--> AI/ML Tests
     |
     +--> Integration CI
            |
            +--> Frontend Build
            +--> Backend Startup
            +--> Frontend Startup
            +--> Health Check
            +--> Authentication Smoke Test

                    |
                    v

             Peer Review / Merge
```

This structure provides validation at both the individual subsystem level and
the frontend-backend integration boundary.
