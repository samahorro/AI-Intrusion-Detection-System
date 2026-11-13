from backend.app.auth.validation import (
    hash_password,
    validate_password,
    validate_username,
    verify_password,
)


def test_validate_username_rejects_empty_username():
    valid, message = validate_username("")

    assert valid is False
    assert message == "Username is required."


def test_validate_username_rejects_too_short_username():
    valid, message = validate_username("ab")

    assert valid is False
    assert (
        message
        == "Username must be at least 3 characters."
    )


def test_validate_username_rejects_too_long_username():
    valid, message = validate_username(
        "a" * 51
    )

    assert valid is False
    assert (
        message
        == "Username must be 50 characters or fewer."
    )


def test_validate_username_rejects_invalid_characters():
    valid, message = validate_username(
        "bad username!"
    )

    assert valid is False
    assert message == (
        "Username may contain only letters, "
        "numbers, underscores, and hyphens."
    )


def test_validate_username_accepts_valid_username():
    valid, message = validate_username(
        "valid_user-123"
    )

    assert valid is True
    assert message is None


def test_validate_username_trims_whitespace():
    valid, message = validate_username(
        "  validuser  "
    )

    assert valid is True
    assert message is None


def test_validate_password_rejects_empty_password():
    valid, message = validate_password("")

    assert valid is False
    assert message == "Password is required."


def test_validate_password_rejects_short_password():
    valid, message = validate_password(
        "Short1!"
    )

    assert valid is False
    assert (
        message
        == "Password must be at least 12 characters."
    )


def test_validate_password_requires_uppercase():
    valid, message = validate_password(
        "lowercase123!"
    )

    assert valid is False
    assert (
        message
        == "Password must contain an uppercase letter."
    )


def test_validate_password_requires_lowercase():
    valid, message = validate_password(
        "UPPERCASE123!"
    )

    assert valid is False
    assert (
        message
        == "Password must contain a lowercase letter."
    )


def test_validate_password_requires_number():
    valid, message = validate_password(
        "NoNumberPassword!"
    )

    assert valid is False
    assert (
        message
        == "Password must contain a number."
    )


def test_validate_password_requires_special_character():
    valid, message = validate_password(
        "NoSpecialPassword123"
    )

    assert valid is False
    assert (
        message
        == "Password must contain a special character."
    )


def test_validate_password_accepts_valid_password():
    valid, message = validate_password(
        "ValidPassword123!"
    )

    assert valid is True
    assert message is None


def test_hash_and_verify_password():
    password = "ValidPassword123!"

    hashed = hash_password(password)

    assert hashed != password

    assert verify_password(
        password,
        hashed,
    ) is True

    assert verify_password(
        "WrongPassword123!",
        hashed,
    ) is False