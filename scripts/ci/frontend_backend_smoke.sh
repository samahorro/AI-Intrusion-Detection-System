

require(
    status == {
        "running": False,
        "interface": None,
    },
    "/capture/status",
)

require(
    stats.get("running") is False,
    "capture must be stopped",
)

require(
    stats.get("interface") is None,
    "capture interface must be null",
)

for field in (
    "packet_count",
    "total_bytes",
    "observed_source_ips",
):
    require(
        type(stats.get(field)) is int
        and stats[field] == 0,
        f"/capture/stats {field} must be zero",
    )

for field, expected_type in (
    ("protocols", dict),
    ("top_source_ips", list),
    ("recent_packets", list),
):
    require(
        isinstance(
            stats.get(field),
            expected_type,
        ),
        f"/capture/stats {field} has unexpected type",
    )

require(
    stats.get("last_packet_at") is None,
    "unexpected last packet",
)

require(
    stats.get("last_error") is None,
    "unexpected capture error",
)

require(
    flows.get("status") == "preview_only",
    "flow preview status",
)

require(
    flows.get("window_packets") == 0,
    "flow window not empty",
)

require(
    flows.get("flow_count") == 0,
    "flow count not zero",
)

require(
    flows.get("flows") == [],
    "unexpected preview flows",
)

require(
    isinstance(
        flows.get("feature_order"),
        list,
    )
    and len(flows["feature_order"]) > 0
    and all(
        isinstance(name, str)
        for name in flows["feature_order"]
    ),
    "invalid flow feature order",
)

print(
    "Authenticated capture status, statistics, "
    "and flow preview contracts validated."
)
PY_CAPTURE

LOGOUT_RESPONSE="$(
  curl \
    --fail \
    --silent \
    --show-error \
    -b "${COOKIE_FILE}" \
    -c "${COOKIE_FILE}" \
    -X POST \
    "${BACKEND_URL}/auth/logout"
)"

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

echo "=== Verifying session is cleared ==="

POST_LOGOUT_STATUS="$(
  curl \
    --silent \
    --output /dev/null \
    --write-out "%{http_code}" \
    -b "${COOKIE_FILE}" \
    "${BACKEND_URL}/auth/me"
)"

if [[ "${POST_LOGOUT_STATUS}" != "401" ]]; then
  echo \
    "Expected /auth/me to return 401 after logout; got ${POST_LOGOUT_STATUS}." \
    >&2
  exit 1
fi

echo "Session removal validated."

echo
echo "Frontend-backend smoke test passed."