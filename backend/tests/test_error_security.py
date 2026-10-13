VALID_PASSWORD = "ValidPassword123!"


def test_registration_response_does_not_expose_password(
    client,
):
    response = client.post(
        "/auth/register",
        json={
            "username": "securityregister",
            "password": VALID_PASSWORD,
        },
    )

    assert response.status_code == 201

    response_text = response.text

    assert VALID_PASSWORD not in response_text
    assert "password_hash" not in response_text


def test_login_response_does_not_expose_password(
    client,
):
    client.post(
        "/auth/register",
        json={
            "username": "securitylogin",
            "password": VALID_PASSWORD,
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "username": "securitylogin",
            "password": VALID_PASSWORD,
        },
    )

    assert response.status_code == 200

    response_text = response.text

    assert VALID_PASSWORD not in response_text
    assert "password_hash" not in response_text


def test_me_response_does_not_expose_password_hash(
    client,
):
    client.post(
        "/auth/register",
        json={
            "username": "securityme",
            "password": VALID_PASSWORD,
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "username": "securityme",
            "password": VALID_PASSWORD,
        },
    )

    assert login_response.status_code == 200

    response = client.get("/auth/me")

    assert response.status_code == 200

    response_text = response.text

    assert VALID_PASSWORD not in response_text
    assert "password_hash" not in response_text


def test_unknown_user_and_wrong_password_use_same_error(
    client,
):
    client.post(
        "/auth/register",
        json={
            "username": "securityuser",
            "password": VALID_PASSWORD,
        },
    )

    unknown_user_response = client.post(
        "/auth/login",
        json={
            "username": "doesnotexist",
            "password": VALID_PASSWORD,
        },
    )

    wrong_password_response = client.post(
        "/auth/login",
        json={
            "username": "securityuser",
            "password": "WrongPassword123!",
        },
    )

    assert unknown_user_response.status_code == 401
    assert wrong_password_response.status_code == 401

    assert (
        unknown_user_response.json()["detail"]
        == wrong_password_response.json()["detail"]
    )

    assert (
        unknown_user_response.json()["detail"]
        == "Invalid username or password."
    )


def test_unauthenticated_error_does_not_expose_internals(
    client,
):
    response = client.get("/auth/me")

    assert response.status_code == 401

    response_text = response.text.lower()

    assert "traceback" not in response_text
    assert "sqlalchemy" not in response_text
    assert "password_hash" not in response_text
    assert "secret_key" not in response_text


def test_registration_validation_error_does_not_echo_password(
    client,
):
    sensitive_password = "DoNotLeakThisPassword123!"

    response = client.post(
        "/auth/register",
        json={
            "password": sensitive_password,
        },
    )

    assert response.status_code == 422
    assert sensitive_password not in response.text


def test_login_validation_error_does_not_echo_password(
    client,
):
    sensitive_password = "DoNotLeakThisLoginPassword123!"

    response = client.post(
        "/auth/login",
        json={
            "password": sensitive_password,
        },
    )

    assert response.status_code == 422
    assert sensitive_password not in response.text