import pytest
from sqlalchemy import inspect

from backend.app.auth.validation import verify_password
from backend.app.models.user import User

VALID_PASSWORD = "ValidPassword123!"


def test_database_initialization(db_session):
    """Verify that the users table is created."""

    inspector = inspect(db_session.bind)

    assert "users" in inspector.get_table_names()


def test_registration_success(client):
    """A user with valid information can register."""

    response = client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "password": VALID_PASSWORD,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["message"] == "User registered successfully."
    assert data["user"]["username"] == "newuser"
    assert "password_hash" not in data["user"]


def test_user_saved_to_database(
    client,
    db_session,
):
    """Registration stores the user in the database."""

    response = client.post(
        "/auth/register",
        json={
            "username": "databaseuser",
            "password": VALID_PASSWORD,
        },
    )

    assert response.status_code == 201

    user = (
        db_session.query(User)
        .filter(User.username == "databaseuser")
        .first()
    )

    assert user is not None
    assert user.username == "databaseuser"


def test_duplicate_username_rejected(client):
    """Duplicate usernames cannot be registered."""

    registration_data = {
        "username": "duplicateuser",
        "password": VALID_PASSWORD,
    }

    first_response = client.post(
        "/auth/register",
        json=registration_data,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/auth/register",
        json=registration_data,
    )

    assert second_response.status_code == 409
    assert (
        second_response.json()["detail"]
        == "Username already exists."
    )


@pytest.mark.parametrize(
    "password",
    [
        "Short1!",
        "lowercasepassword1!",
        "UPPERCASEPASSWORD1!",
        "NoNumberPassword!",
        "NoSpecialPassword123",
    ],
)
def test_invalid_password_rejected(
    client,
    password,
):
    """Passwords that do not meet requirements are rejected."""

    response = client.post(
        "/auth/register",
        json={
            "username": "passworduser",
            "password": password,
        },
    )

    assert response.status_code == 400


def test_valid_password_accepted(client):
    """A password meeting all requirements is accepted."""

    response = client.post(
        "/auth/register",
        json={
            "username": "validpassworduser",
            "password": VALID_PASSWORD,
        },
    )

    assert response.status_code == 201


def test_missing_username_rejected(client):
    """Registration requires a username."""

    response = client.post(
        "/auth/register",
        json={
            "password": VALID_PASSWORD,
        },
    )

    assert response.status_code == 422


def test_missing_password_rejected(client):
    """Registration requires a password."""

    response = client.post(
        "/auth/register",
        json={
            "username": "missingpassworduser",
        },
    )

    assert response.status_code == 422


def test_password_is_hashed(
    client,
    db_session,
):
    """The plaintext password is never stored."""

    password = VALID_PASSWORD

    response = client.post(
        "/auth/register",
        json={
            "username": "hasheduser",
            "password": password,
        },
    )

    assert response.status_code == 201

    user = (
        db_session.query(User)
        .filter(User.username == "hasheduser")
        .first()
    )

    assert user is not None
    assert user.password_hash != password
    assert verify_password(
        password,
        user.password_hash,
    )


def test_login_success(client):
    """A registered user can log in."""

    client.post(
        "/auth/register",
        json={
            "username": "loginuser",
            "password": VALID_PASSWORD,
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "username": "loginuser",
            "password": VALID_PASSWORD,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Login successful."
    assert data["user"]["username"] == "loginuser"
    assert "password_hash" not in data["user"]


def test_login_creates_session(client):
    """Successful login creates an authenticated session."""

    client.post(
        "/auth/register",
        json={
            "username": "sessionuser",
            "password": VALID_PASSWORD,
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "username": "sessionuser",
            "password": VALID_PASSWORD,
        },
    )

    assert login_response.status_code == 200

    me_response = client.get("/auth/me")

    assert me_response.status_code == 200
    assert (
        me_response.json()["user"]["username"]
        == "sessionuser"
    )


def test_unknown_user_rejected(client):
    """Login fails when the username does not exist."""

    response = client.post(
        "/auth/login",
        json={
            "username": "unknownuser",
            "password": VALID_PASSWORD,
        },
    )

    assert response.status_code == 401
    assert (
        response.json()["detail"]
        == "Invalid username or password."
    )


def test_wrong_password_rejected(client):
    """Login fails when the password is incorrect."""

    client.post(
        "/auth/register",
        json={
            "username": "wrongpassworduser",
            "password": VALID_PASSWORD,
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "username": "wrongpassworduser",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert (
        response.json()["detail"]
        == "Invalid username or password."
    )


def test_authenticated_user_can_access_me(client):
    """Authenticated users can access the protected /me route."""

    register_response = client.post(
        "/auth/register",
        json={
            "username": "authenticateduser",
            "password": VALID_PASSWORD,
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "username": "authenticateduser",
            "password": VALID_PASSWORD,
        },
    )

    assert login_response.status_code == 200

    response = client.get("/auth/me")

    assert response.status_code == 200

    data = response.json()["user"]

    assert data["username"] == "authenticateduser"
    assert "password_hash" not in data


def test_unauthenticated_user_cannot_access_me(
    client,
):
    """Users without a session cannot access /me."""

    response = client.get("/auth/me")

    assert response.status_code == 401
    assert (
        response.json()["detail"]
        == "Authentication required."
    )


def test_logout(client):
    """A logged-in user can log out."""

    client.post(
        "/auth/register",
        json={
            "username": "logoutuser",
            "password": VALID_PASSWORD,
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "username": "logoutuser",
            "password": VALID_PASSWORD,
        },
    )

    assert login_response.status_code == 200

    logout_response = client.post(
        "/auth/logout"
    )

    assert logout_response.status_code == 200
    assert (
        logout_response.json()["message"]
        == "Logout successful."
    )


def test_logout_removes_access_to_protected_route(
    client,
):
    """
    Verify the complete authentication lifecycle:
    register -> login -> protected route -> logout -> rejection.
    """

    register_response = client.post(
        "/auth/register",
        json={
            "username": "logoutintegration",
            "password": VALID_PASSWORD,
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "username": "logoutintegration",
            "password": VALID_PASSWORD,
        },
    )

    assert login_response.status_code == 200

    authenticated_response = client.get(
        "/auth/me"
    )

    assert authenticated_response.status_code == 200

    logout_response = client.post(
        "/auth/logout"
    )

    assert logout_response.status_code == 200

    after_logout_response = client.get(
        "/auth/me"
    )

    assert after_logout_response.status_code == 401
    assert (
        after_logout_response.json()["detail"]
        == "Authentication required."
    )