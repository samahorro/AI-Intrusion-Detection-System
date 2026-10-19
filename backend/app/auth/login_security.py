from datetime import UTC, datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.login_attempt import LoginAttempt

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


def record_login_attempt(
    db: Session,
    username: str,
    success: bool,
    reason: str,
):
    """Store one authentication attempt for auditing."""

    attempt = LoginAttempt(
        username=username,
        success=success,
        reason=reason,
    )

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return attempt


def _failure_window_start(
    db: Session,
    username: str,
):
    """
    Return the point after which failed attempts
    count toward account lockout.
    """

    cutoff = datetime.now(UTC) - timedelta(
        minutes=LOCKOUT_MINUTES,
    )

    latest_success = (
        db.query(
            func.max(LoginAttempt.created_at)
        )
        .filter(
            LoginAttempt.username == username,
            LoginAttempt.success.is_(True),
        )
        .scalar()
    )

    if latest_success is None:
        return cutoff

    if latest_success.tzinfo is None:
        latest_success = latest_success.replace(
            tzinfo=UTC,
        )

    return max(
        cutoff,
        latest_success,
    )


def failed_login_count(
    db: Session,
    username: str,
) -> int:
    """
    Count recent invalid-password attempts
    since the user's most recent successful login.
    """

    window_start = _failure_window_start(
        db,
        username,
    )

    return (
        db.query(LoginAttempt)
        .filter(
            LoginAttempt.username == username,
            LoginAttempt.success.is_(False),
            LoginAttempt.reason
            == "invalid_password",
            LoginAttempt.created_at
            >= window_start,
        )
        .count()
    )


def is_account_locked(
    db: Session,
    username: str,
) -> bool:
    """Return True when the account reached the failure limit."""

    return (
        failed_login_count(
            db,
            username,
        )
        >= MAX_FAILED_ATTEMPTS
    )