import re

from pwdlib import PasswordHash


password_hasher = PasswordHash.recommended()


def validate_username(username: str):
    """Validate a username."""

    if not username:
        return False, "Username is required."

    username = username.strip()

    if len(username) < 3:
        return (
            False,
            "Username must be at least 3 characters.",
        )

    if len(username) > 50:
        return (
            False,
            "Username must be 50 characters or fewer.",
        )

    if not re.fullmatch(
        r"[A-Za-z0-9_-]+",
        username,
    ):
        return (
            False,
            (
                "Username may contain only letters, "
                "numbers, underscores, and hyphens."
            ),
        )

    return True, None


def validate_password(password: str):
    """Validate password security requirements."""

    if not password:
        return False, "Password is required."

    if len(password) < 12:
        return (
            False,
            "Password must be at least 12 characters.",
        )

    if not re.search(r"[A-Z]", password):
        return (
            False,
            "Password must contain an uppercase letter.",
        )

    if not re.search(r"[a-z]", password):
        return (
            False,
            "Password must contain a lowercase letter.",
        )

    if not re.search(r"\d", password):
        return (
            False,
            "Password must contain a number.",
        )

    if not re.search(r"[^A-Za-z0-9]", password):
        return (
            False,
            "Password must contain a special character.",
        )

    return True, None


def hash_password(password: str):
    """Securely hash a password."""

    return password_hasher.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
):
    """Check a password against its stored hash."""

    return password_hasher.verify(
        plain_password,
        hashed_password,
    )