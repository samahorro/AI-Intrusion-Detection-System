
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./backend/app.db",
)

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False,
    }


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    """Provide a database session to FastAPI routes."""

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def seed_default_user():
    """Create the configured development user if needed."""

    from .auth.validation import (
        hash_password,
        validate_password,
        validate_username,
    )
    from .models.user import User

    username = os.getenv(
        "DEFAULT_USERNAME",
        "",
    ).strip()

    password = os.getenv(
        "DEFAULT_PASSWORD",
        "",
    )

    if not username or not password:
        return False

    username_valid, username_error = (
        validate_username(username)
    )

    if not username_valid:
        raise RuntimeError(
            "Invalid DEFAULT_USERNAME: "
            f"{username_error}"
        )

    password_valid, password_error = (
        validate_password(password)
    )

    if not password_valid:
        raise RuntimeError(
            "Invalid DEFAULT_PASSWORD: "
            f"{password_error}"
        )

    db = SessionLocal()

    try:
        existing_user = (
            db.query(User)
            .filter(
                User.username == username
            )
            .first()
        )

        if existing_user is not None:
            return False

        user = User(
            username=username,
            password_hash=hash_password(
                password
            ),
        )

        db.add(user)
        db.commit()

        return True

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def init_db():
    """Create database tables and seed configured users."""

    from .models.blocked_ip import BlockedIP  # noqa: F401
    from .models.login_attempt import LoginAttempt  # noqa: F401
    from .models.network_event import NetworkEvent  # noqa: F401
    from .models.user import User  # noqa: F401

    Base.metadata.create_all(
        bind=engine
    )

    seed_default_user()
