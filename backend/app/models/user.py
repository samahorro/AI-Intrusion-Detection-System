from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash = Column(
        String(255),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        """Return user data safe for API responses."""

        return {
            "id": self.id,
            "username": self.username,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
        }