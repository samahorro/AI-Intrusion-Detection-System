
"""Additional security regression tests for user registration."""

from backend.app.models.user import User

VALID_PASSWORD = "ValidPassword123!"


def test_registration_does_not_automatically_log_in(client):
    """Creating an account should not create an authenticated session."""

    response = client.post(
        "/auth/register",
        json={
            "username": "registration_only_user",
            "password": VALID_PASSWORD,
        },
    )

    assert response.status_code == 201

    protected_response = client.get("/auth/me")

    assert protected_response.status_code == 401
    assert (
        protected_response.json()["detail"]
        == "Authentication required."
    )


def test_registration_normalizes_username_before_duplicate_check(
    client,
):
    """Whitespace cannot be used to register a duplicate username."""

    first_response = client.post(
        "/auth/register",
        json={
            "username": "  normalized_user  ",
            "password": VALID_PASSWORD,
        },
    )

    assert first_response.status_code == 201
    assert (
        first_response.json()["user"]["username"]
        == "normalized_user"
    )

    duplicate_response = client.post(
        "/auth/register",
        json={
            "username": "normalized_user",
            "password": VALID_PASSWORD,
        },
    )

    assert duplicate_response.status_code == 409
    assert (
        duplicate_response.json()["detail"]
        == "Username already exists."
    )


def test_invalid_registration_does_not_create_database_user(
    client,
    db_session,
):
    """Rejecting a weak password must not create a user account."""

    response = client.post(
        "/auth/register",
        json={
            "username": "invalid_registration_user",
            "password": "short",
        },
    )

    assert response.status_code == 400

    saved_user = (
        db_session.query(User)
        .filter(
            User.username == "invalid_registration_user"
        )
        .first()
    )

    assert saved_user is None
