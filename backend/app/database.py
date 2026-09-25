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


def init_db():
    """Create all database tables."""

    # Import models before create_all().
    from .models.user import User  # noqa: F401

    Base.metadata.create_all(bind=engine)