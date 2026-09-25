import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base, get_db
from backend.app.main import create_app


@pytest.fixture
def test_engine(tmp_path):
    """Create an isolated SQLite database."""

    database_file = (
        tmp_path / "authentication_test.db"
    )

    engine = create_engine(
        f"sqlite:///{database_file}",
        connect_args={
            "check_same_thread": False,
        },
    )

    Base.metadata.create_all(bind=engine)

    yield engine

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def session_factory(test_engine):
    """Create database sessions for tests."""

    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )


@pytest.fixture
def app(session_factory):
    """Create an isolated FastAPI application."""

    application = create_app(
        initialize_database=False,
    )

    def override_get_db():
        db = session_factory()

        try:
            yield db
        finally:
            db.close()

    application.dependency_overrides[
        get_db
    ] = override_get_db

    yield application

    application.dependency_overrides.clear()


@pytest.fixture
def client(app):
    """Create a FastAPI test client."""

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session(session_factory):
    """Provide direct database access to tests."""

    db = session_factory()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_user():
    """Reusable valid user information."""

    return {
        "username": "testuser",
        "password": "StrongPassword123!",
    }


@pytest.fixture
def registered_user(
    client,
    sample_user,
):
    """Create a registered user."""

    response = client.post(
        "/auth/register",
        json=sample_user,
    )

    assert response.status_code == 201

    return sample_user