from backend.app.models.login_attempt import LoginAttempt

VALID_PASSWORD = "ValidPassword123!"
WRONG_PASSWORD = "WrongPassword123!"


def register_user(
    client,
    username: str,
):
    """Create a valid user for login-security tests."""

    response = client.post(
        "/auth/register",
        json={
            "username": username,
            "password": VALID_PASSWORD,
        },
    )

    assert response.status_code == 201


def test_failed_login_is_recorded(
    client,
    db_session,
):
    """A failed password attempt is stored for auditing."""

    register_user(
        client,
        "audituser",
    )

    response = client.post(
        "/auth/login",
        json={
            "username": "audituser",
            "password": WRONG_PASSWORD,
        },
    )

    assert response.status_code == 401

    attempt = (
        db_session.query(
            LoginAttempt
        )
        .filter(
            LoginAttempt.username
            == "audituser"
        )
        .first()
    )

    assert attempt is not None
    assert attempt.success is False
    assert (
        attempt.reason
        == "invalid_password"
    )


def test_successful_login_is_recorded(
    client,
    db_session,
):
    """A successful login is stored for auditing."""

    register_user(
        client,
        "successaudit",
    )

    response = client.post(
        "/auth/login",
        json={
            "username": "successaudit",
            "password": VALID_PASSWORD,
        },
    )

    assert response.status_code == 200

    attempt = (
        db_session.query(
            LoginAttempt
        )
        .filter(
            LoginAttempt.username
            == "successaudit",
            LoginAttempt.success.is_(
                True
            ),
        )
        .first()
    )

    assert attempt is not None
    assert (
        attempt.reason
        == "login_success"
    )


def test_unknown_username_attempt_is_recorded(
    client,
    db_session,
):
    """
    Unknown usernames are logged without
    exposing whether an account exists.
    """

    response = client.post(
        "/auth/login",
        json={
            "username": "notarealuser",
            "password": VALID_PASSWORD,
        },
    )

    assert response.status_code == 401

    assert (
        response.json()["detail"]
        == "Invalid username or password."
    )

    attempt = (
        db_session.query(
            LoginAttempt
        )
        .filter(
            LoginAttempt.username
            == "notarealuser"
        )
        .first()
    )

    assert attempt is not None
    assert attempt.success is False

    assert (
        attempt.reason
        == "unknown_username"
    )


def test_account_locked_after_five_failed_passwords(
    client,
):
    """
    Five failed password attempts
    temporarily lock an account.
    """

    register_user(
        client,
        "lockeduser",
    )

    for attempt_number in range(5):
        response = client.post(
            "/auth/login",
            json={
                "username": "lockeduser",
                "password": WRONG_PASSWORD,
            },
        )

        if attempt_number < 4:
            assert (
                response.status_code
                == 401
            )

    assert response.status_code == 423

    assert (
        response.json()["detail"]
        == (
            "Account temporarily locked due to "
            "too many failed login attempts."
        )
    )


def test_locked_account_rejects_correct_password(
    client,
):
    """
    A locked account stays locked until
    the temporary lockout expires.
    """

    register_user(
        client,
        "stilllocked",
    )

    for _ in range(5):
        client.post(
            "/auth/login",
            json={
                "username": "stilllocked",
                "password": WRONG_PASSWORD,
            },
        )

    response = client.post(
        "/auth/login",
        json={
            "username": "stilllocked",
            "password": VALID_PASSWORD,
        },
    )

    assert response.status_code == 423


def test_successful_login_resets_failure_sequence(
    client,
):
    """
    Failures before the most recent successful
    login do not count toward a new lockout.
    """

    register_user(
        client,
        "resetuser",
    )

    for _ in range(3):
        response = client.post(
            "/auth/login",
            json={
                "username": "resetuser",
                "password": WRONG_PASSWORD,
            },
        )

        assert (
            response.status_code
            == 401
        )

    success_response = client.post(
        "/auth/login",
        json={
            "username": "resetuser",
            "password": VALID_PASSWORD,
        },
    )

    assert (
        success_response.status_code
        == 200
    )

    for _ in range(4):
        response = client.post(
            "/auth/login",
            json={
                "username": "resetuser",
                "password": WRONG_PASSWORD,
            },
        )

        assert (
            response.status_code
            == 401
        )

    final_success = client.post(
        "/auth/login",
        json={
            "username": "resetuser",
            "password": VALID_PASSWORD,
        },
    )

    assert (
        final_success.status_code
        == 200
    )