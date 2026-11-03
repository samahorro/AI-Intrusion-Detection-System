
"""KAN-230: Protected IP management API tests."""

import secrets

from fastapi.testclient import TestClient

from backend.app.main import app


def create_authenticated_client():
    """Register and log in a unique test user."""

    client = TestClient(app)

    username = "s4api_" + secrets.token_hex(8)
    password = "S4!" + secrets.token_urlsafe(20)

    registration = client.post(
        "/auth/register",
        json={
            "username": username,
            "password": password,
        },
    )
    assert registration.status_code == 201

    login = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )
    assert login.status_code == 200

    return client


def create_unique_block(client, reason="Security test"):
    """Find an unused documentation IP and create a block.

    The current test database may retain records from
    previous runs. A 404 ownership conflict means the IP
    already belongs to a different test user.
    """

    prefixes = (
        "192.0.2",
        "198.51.100",
        "203.0.113",
    )

    for _ in range(100):
        prefix = secrets.choice(prefixes)
        address = f"{prefix}.{secrets.randbelow(254) + 1}"

        response = client.post(
            "/blocked-ips",
            json={
                "ip_address": address,
                "reason": reason,
            },
        )

        if response.status_code == 201:
            return address, response

        if (
            response.status_code == 404
            and response.json().get("detail")
            == "IP record not found."
        ):
            continue

        raise AssertionError(
            f"Unexpected block response: "
            f"{response.status_code} "
            f"{response.text}"
        )

    raise AssertionError(
        "Could not find an unused test IP address."
    )


def test_ip_endpoints_require_login():
    """All management endpoints require authentication."""

    with TestClient(app) as client:
        assert client.get("/blocked-ips").status_code == 401

        assert client.post(
            "/blocked-ips",
            json={"ip_address": "192.0.2.51"},
        ).status_code == 401

        assert client.delete(
            "/blocked-ips/192.0.2.51"
        ).status_code == 401


def test_authenticated_user_can_block_ip():
    """Authenticated users can create simulated blocks."""

    with create_authenticated_client() as client:
        address, response = create_unique_block(client)

        assert response.status_code == 201
        assert response.json()["success"] is True
        assert address is not None


def test_authenticated_user_can_list_blocks():
    """Users can list records belonging to their account."""

    with create_authenticated_client() as client:
        address, created = create_unique_block(
            client,
            reason="List endpoint test",
        )

        assert created.status_code == 201

        response = client.get("/blocked-ips")

        assert response.status_code == 200

        addresses = [
            item["ip_address"]
            for item in response.json()["items"]
        ]

        assert address in addresses


def test_invalid_ip_is_rejected():
    """Reject malformed IP addresses."""

    with create_authenticated_client() as client:
        response = client.post(
            "/blocked-ips",
            json={
                "ip_address": "192.0.2.5;whoami",
            },
        )

        assert response.status_code == 400


def test_authenticated_user_can_unblock_ip():
    """Users can unblock their own IP records."""

    with create_authenticated_client() as client:
        address, created = create_unique_block(client)

        assert created.status_code == 201

        response = client.delete(
            f"/blocked-ips/{address}"
        )

        assert response.status_code == 200


def test_user_cannot_unblock_another_users_ip():
    """Users cannot manage another user's private record."""

    with (
        create_authenticated_client() as user_a,
        create_authenticated_client() as user_b,
    ):
        address, created = create_unique_block(user_a)

        assert created.status_code == 201

        # User B must not see User A's saved record.
        listing = user_b.get("/blocked-ips")

        assert listing.status_code == 200

        user_b_addresses = [
            item["ip_address"]
            for item in listing.json()["items"]
        ]

        assert address not in user_b_addresses

        # User B must not unblock User A's record.
        denied_delete = user_b.delete(
            f"/blocked-ips/{address}"
        )

        assert denied_delete.status_code == 404

        # User B must not overwrite User A's record.
        denied_post = user_b.post(
            "/blocked-ips",
            json={"ip_address": address},
        )

        assert denied_post.status_code == 404

        # User A must still have access to the record.
        owner_listing = user_a.get("/blocked-ips")

        assert owner_listing.status_code == 200

        owner_addresses = [
            item["ip_address"]
            for item in owner_listing.json()["items"]
        ]

        assert address in owner_addresses
