
"""Database records for blocked IP addresses.

Stores IP blocking information but does not modify
real firewall rules.
"""

from datetime import UTC, datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import validates

from backend.app.database import Base
from backend.app.ip_management.validation import validate_ip_address


class BlockedIP(Base):
    """Store blocked IP records in the database."""

    __tablename__ = "blocked_ips"

    __table_args__ = (
        CheckConstraint(
            "block_type IN ('permanent', 'temporary')",
            name="ck_blocked_ips_block_type",
        ),
        CheckConstraint(
            "status IN ('blocked', 'unblocked')",
            name="ck_blocked_ips_status",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    ip_address = Column(
        String(45),
        nullable=False,
        unique=True,
        index=True,
    )

    block_type = Column(
        String(16),
        nullable=False,
        default="permanent",
    )

    reason = Column(
        String(255),
        nullable=True,
    )

    status = Column(
        String(16),
        nullable=False,
        default="blocked",
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_by_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    @validates("ip_address")
    def normalize_ip_address(self, _key, value):
        """Validate and normalize stored IP addresses."""
        return validate_ip_address(value)
