#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(
  cd "$(dirname "${BASH_SOURCE[0]}")/../.."
  pwd
)"

BACKEND_HOST="${BACKEND_HOST:-127.0.0.1}"
BACKEND_PORT="${BACKEND_PORT:-8000}"

FRONTEND_HOST="${FRONTEND_HOST:-127.0.0.1}"
FRONTEND_PORT="${FRONTEND_PORT:-4173}"

BACKEND_URL="http://${BACKEND_HOST}:${BACKEND_PORT}"
FRONTEND_URL="http://${FRONTEND_HOST}:${FRONTEND_PORT}"

BACKEND_LOG="${TMPDIR:-/tmp}/ai-ids-backend-smoke.log"
FRONTEND_LOG="${TMPDIR:-/tmp}/ai-ids-frontend-smoke.log"
DATABASE_FILE="${TMPDIR:-/tmp}/ai-ids-smoke.db"

BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  local exit_code=$?

  if [[ -n "${FRONTEND_PID}" ]]; then
    kill "${FRONTEND_PID}" 2>/dev/null || true
  fi

  if [[ -n "${BACKEND_PID}" ]]; then
    kill "${BACKEND_PID}" 2>/dev/null || true
  fi

  rm -f "${DATABASE_FILE}"

  exit "${exit_code}"
}

trap cleanup EXIT INT TERM

wait_for_url() {
  local name="$1"
  local url="$2"
  local attempts="${3:-30}"

  echo "Waiting for ${name}: ${url}"

  for ((attempt = 1; attempt <= attempts; attempt++)); do
    if curl --fail --silent --show-error "${url}" >/dev/null; then
      echo "${name} is ready."
      return 0
    fi

    sleep 1
  done

  echo "${name} did not become ready." >&2

  if [[ "${name}" == "backend" ]]; then
    cat "${BACKEND_LOG}" >&2 || true
  else
    cat "${FRONTEND_LOG}" >&2 || true
  fi

  return 1
}

cd "${ROOT_DIR}"

echo "=== Building frontend ==="

npm --prefix frontend run build

echo "=== Starting backend ==="

DATABASE_URL="sqlite:///${DATABASE_FILE}" \
  python3 -m uvicorn backend.app.main:app \
    --host "${BACKEND_HOST}" \
    --port "${BACKEND_PORT}" \
    >"${BACKEND_LOG}" 2>&1 &

BACKEND_PID=$!

echo "=== Starting frontend preview ==="

npm --prefix frontend run preview -- \
  --host "${FRONTEND_HOST}" \
  --port "${FRONTEND_PORT}" \
  >"${FRONTEND_LOG}" 2>&1 &

FRONTEND_PID=$!

wait_for_url \
  "backend" \
  "${BACKEND_URL}/health"

wait_for_url \
  "frontend" \
  "${FRONTEND_URL}/"

echo "=== Verifying backend health contract ==="

HEALTH_RESPONSE="$(
  curl \
    --fail \
    --silent \
    --show-error \
    "${BACKEND_URL}/health"
)"

python3 - "${HEALTH_RESPONSE}" <<'PY'
import json
import sys

response = json.loads(sys.argv[1])

if response.get("status") != "ok":
    raise SystemExit(
        f"Unexpected health response: {response}"
    )

print("Backend health response validated.")
PY

echo "=== Verifying frontend HTML ==="

FRONTEND_RESPONSE="$(
  curl \
    --fail \
    --silent \
    --show-error \
    "${FRONTEND_URL}/"
)"

if ! grep -q 'id="root"' <<< "${FRONTEND_RESPONSE}"; then
  echo "Frontend root element was not found." >&2
  exit 1
fi

echo "Frontend root document validated."

echo "=== Verifying authentication API contract ==="

SMOKE_USERNAME="smoke_${GITHUB_RUN_ID:-local}_$$"
SMOKE_PASSWORD="StrongPassword123!"

REGISTER_RESPONSE="$(
  curl \
    --fail \
    --silent \
    --show-error \
    -X POST \
    -H "Content-Type: application/json" \
    -d "{
      \"username\": \"${SMOKE_USERNAME}\",
      \"password\": \"${SMOKE_PASSWORD}\"
    }" \
    "${BACKEND_URL}/auth/register"
)"

python3 - "${REGISTER_RESPONSE}" "${SMOKE_USERNAME}" <<'PY'
import json
import sys

response = json.loads(sys.argv[1])
expected_username = sys.argv[2]

user = response.get("user", {})

if user.get("username") != expected_username:
    raise SystemExit(
        f"Unexpected registration response: {response}"
    )

print("Registration contract validated.")
PY

COOKIE_FILE="$(
  mktemp "${TMPDIR:-/tmp}/ai-ids-cookie.XXXXXX"
)"

LOGIN_RESPONSE="$(
  curl \
    --fail \
    --silent \
    --show-error \
    -c "${COOKIE_FILE}" \
    -X POST \
    -H "Content-Type: application/json" \
    -d "{
      \"username\": \"${SMOKE_USERNAME}\",
      \"password\": \"${SMOKE_PASSWORD}\"
    }" \
    "${BACKEND_URL}/auth/login"
)"

python3 - "${LOGIN_RESPONSE}" "${SMOKE_USERNAME}" <<'PY'
import json
import sys

response = json.loads(sys.argv[1])
expected_username = sys.argv[2]

user = response.get("user", {})

if response.get("message") != "Login successful.":
    raise SystemExit(
        f"Unexpected login response: {response}"
    )

if user.get("username") != expected_username:
    raise SystemExit(
        f"Unexpected login user: {response}"
    )

print("Login contract validated.")
PY

LOGOUT_RESPONSE="$(
  curl \
    --fail \
    --silent \
    --show-error \
    -b "${COOKIE_FILE}" \
    -X POST \
    "${BACKEND_URL}/auth/logout"
)"

rm -f "${COOKIE_FILE}"

python3 - "${LOGOUT_RESPONSE}" <<'PY'
import json
import sys

response = json.loads(sys.argv[1])

if response.get("message") != "Logout successful.":
    raise SystemExit(
        f"Unexpected logout response: {response}"
    )

print("Logout contract validated.")
PY

echo
echo "Frontend-backend smoke test passed."
