from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class NetworkEvent(Base):
    """Persisted network event captured by the backend."""

    __tablename__ = "network_events"

    event_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    session_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    timestamp: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    src_ip: Mapped[str] = mapped_column(
        String(45),
        nullable=False,
    )

    dest_ip: Mapped[str] = mapped_column(
        String(45),
        nullable=False,
    )

    protocol: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )

    src_port: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    dest_port: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    payload_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    direction: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )