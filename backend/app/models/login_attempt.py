from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from ..database import Base


class LoginAttempt(Base):
    """Store authentication attempts for security auditing."""

    __tablename__ = "login_attempts"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    username = Column(
        String(50),
        nullable=False,
        index=True,
    )

    success = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    reason = Column(
        String(100),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        index=True,
    )