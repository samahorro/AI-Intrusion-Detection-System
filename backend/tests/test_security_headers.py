
"""Sprint 4: Backend security header regression tests.

SOC 2 CC6.1 - Logical Access Security.

Verify that security headers are returned on successful
and unauthorized requests and that sensitive request
values are not exposed in validation errors.
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.mark.parametrize(
    ("path", "expected_status"),
    [
        ("/health", 200),
        ("/auth/me", 401),
        ("/capture/status", 401),
    ],
)
def test_security_headers(
    path: str,
    expected_status: int,
):
    """Security headers must protect API responses."""

    with TestClient(app) as client:
        response = client.get(path)

    assert response.status_code == expected_status

    assert (
        response.headers["x-content-type-options"]
        == "nosniff"
    )

    assert (
        response.headers["x-frame-options"]
        == "DENY"
    )

    assert (
        response.headers["referrer-policy"]
        == "no-referrer"
    )

    assert (
        response.headers["cache-control"]
        == "no-store"
    )


def test_validation_error_does_not_expose_sensitive_input():
    """Validation errors must not echo sensitive request data."""

    sensitive_value = "PRIVATE_TEST_VALUE_DO_NOT_EXPOSE"

    with TestClient(app) as client:
        response = client.post(
            "/auth/register",
            json={
                "username": "security_test",
                "password": {
                    "value": sensitive_value,
                },
            },
        )

    assert response.status_code == 422

    assert sensitive_value not in response.text
