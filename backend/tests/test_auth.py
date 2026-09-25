import pytest
from sqlalchemy import inspect

from backend.app.models.user import User


def test_database_initialization(
    test_engine,
):
    inspector = inspect(test_engine)

    tables = inspector.get_table_names()

    assert "users" in tables


def test_registration_success(
    client,
    sample_user,
):
    response = client.post(
        "/auth/register",
        json=sample_user,
    )

    assert response.status_code == 201

    data = response.json()

    assert (
        data["message"]
        == "User registered successfully."
    )

    assert (
        data["user"]["username"]
        == sample_user["username"]
    )

    assert "password" not in data["user"]

    assert "password_hash" not in data["user"]


def test_user_saved_to_database(
    client,
    db_session,
    sample_user,
):
    response = client.post(
        "/auth/register",
        json=sample_user,
    )

    assert response.status_code == 201

    user = (
        db_session.query(User)
        .filter(
            User.username
            == sample_user["username"]
        )
        .first()
    )

    assert user is not None


def test_duplicate_username_rejected(
    client,
    registered_user,
):
    response = client.post(
        "/auth/register",
        json=registered_user,
    )

    assert response.status_code == 409

    assert (
        response.json()["detail"]
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
    response = client.post(
        "/auth/register",
        json={
            "username": "passwordtest",
            "password": password,
        },
    )

    assert response.status_code == 400


def test_valid_password_accepted(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "validuser",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 201


def test_missing_username_rejected(client):
    response = client.post(
        "/auth/register",
        json={
            "password": "StrongPassword123!",
        },
    )

    # FastAPI/Pydantic validation error.
    assert response.status_code == 422


def test_missing_password_rejected(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
        },
    )

    assert response.status_code == 422


def test_password_is_hashed(
    client,
    db_session,
    sample_user,
):
    response = client.post(
        "/auth/register",
        json=sample_user,
    )

    assert response.status_code == 201

    user = (
        db_session.query(User)
        .filter(
            User.username
            == sample_user["username"]
        )
        .first()
    )

    assert user is not None

    assert (
        user.password_hash
        != sample_user["password"]
    )

    assert len(user.password_hash) > 20


def test_login_success(
    client,
    registered_user,
):
    response = client.post(
        "/auth/login",
        json=registered_user,
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["message"]
        == "Login successful."
    )

    assert (
        data["user"]["username"]
        == registered_user["username"]
    )


def test_login_creates_session(
    client,
    registered_user,
):
    response = client.post(
        "/auth/login",
        json=registered_user,
    )

    assert response.status_code == 200

    assert "session" in client.cookies


def test_invalid_password_rejected(
    client,
    registered_user,
):
    response = client.post(
        "/auth/login",
        json={
            "username":
                registered_user["username"],
            "password":
                "WrongPassword123!",
        },
    )

    assert response.status_code == 401

    assert (
        response.json()["detail"]
        == "Invalid username or password."
    )


def test_unknown_user_rejected(client):
    response = client.post(
        "/auth/login",
        json={
            "username": "unknownuser",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 401


def test_logout(
    client,
    registered_user,
):
    login_response = client.post(
        "/auth/login",
        json=registered_user,
    )

    assert login_response.status_code == 200

    assert "session" in client.cookies

    logout_response = client.post(
        "/auth/logout",
    )

    assert logout_response.status_code == 200

    assert logout_response.json() == {
        "message": "Logout successful.",
    }