import pytest

from backend.app import database
from backend.app.auth.validation import verify_password
from backend.app.models.user import User


def test_seed_default_user_skips_when_credentials_missing(
    monkeypatch,
):
    monkeypatch.delenv(
        "DEFAULT_USERNAME",
        raising=False,
    )
    monkeypatch.delenv(
        "DEFAULT_PASSWORD",
        raising=False,
    )

    result = database.seed_default_user()

    assert result is False


def test_seed_default_user_rejects_invalid_username(
    monkeypatch,
):
    monkeypatch.setenv(
        "DEFAULT_USERNAME",
        "!!",
    )
    monkeypatch.setenv(
        "DEFAULT_PASSWORD",
        "StrongPassword123!",
    )

    with pytest.raises(
        RuntimeError,
        match="Invalid DEFAULT_USERNAME",
    ):
        database.seed_default_user()


def test_seed_default_user_rejects_invalid_password(
    monkeypatch,
):
    monkeypatch.setenv(
        "DEFAULT_USERNAME",
        "defaultuser",
    )
    monkeypatch.setenv(
        "DEFAULT_PASSWORD",
        "weak",
    )

    with pytest.raises(
        RuntimeError,
        match="Invalid DEFAULT_PASSWORD",
    ):
        database.seed_default_user()


def test_seed_default_user_creates_user(
    monkeypatch,
    session_factory,
):
    monkeypatch.setenv(
        "DEFAULT_USERNAME",
        "defaultuser",
    )
    monkeypatch.setenv(
        "DEFAULT_PASSWORD",
        "StrongPassword123!",
    )

    monkeypatch.setattr(
        database,
        "SessionLocal",
        session_factory,
    )

    result = database.seed_default_user()

    assert result is True

    db = session_factory()

    try:
        user = (
            db.query(User)
            .filter(
                User.username == "defaultuser"
            )
            .one()
        )

        assert user.username == "defaultuser"

        assert verify_password(
            "StrongPassword123!",
            user.password_hash,
        )

        assert (
            user.password_hash
            != "StrongPassword123!"
        )

    finally:
        db.close()


def test_seed_default_user_does_not_duplicate_user(
    monkeypatch,
    session_factory,
):
    monkeypatch.setenv(
        "DEFAULT_USERNAME",
        "defaultuser",
    )
    monkeypatch.setenv(
        "DEFAULT_PASSWORD",
        "StrongPassword123!",
    )

    monkeypatch.setattr(
        database,
        "SessionLocal",
        session_factory,
    )

    first = database.seed_default_user()
    second = database.seed_default_user()

    assert first is True
    assert second is False

    db = session_factory()

    try:
        users = (
            db.query(User)
            .filter(
                User.username == "defaultuser"
            )
            .all()
        )

        assert len(users) == 1

    finally:
        db.close()


def test_seed_default_user_rolls_back_on_commit_failure(
    monkeypatch,
):
    monkeypatch.setenv(
        "DEFAULT_USERNAME",
        "defaultuser",
    )
    monkeypatch.setenv(
        "DEFAULT_PASSWORD",
        "StrongPassword123!",
    )

    state = {
        "rollback_called": False,
        "close_called": False,
        "add_called": False,
    }

    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return None

    class FakeSession:
        def query(self, model):
            return FakeQuery()

        def add(self, user):
            state["add_called"] = True

        def commit(self):
            raise RuntimeError(
                "database commit failed"
            )

        def rollback(self):
            state["rollback_called"] = True

        def close(self):
            state["close_called"] = True

    monkeypatch.setattr(
        database,
        "SessionLocal",
        FakeSession,
    )

    with pytest.raises(
        RuntimeError,
        match="database commit failed",
    ):
        database.seed_default_user()

    assert state["add_called"] is True
    assert state["rollback_called"] is True
    assert state["close_called"] is True


def test_get_db_closes_session(
    monkeypatch,
):
    state = {
        "closed": False,
    }

    class FakeSession:
        def close(self):
            state["closed"] = True

    fake_session = FakeSession()

    monkeypatch.setattr(
        database,
        "SessionLocal",
        lambda: fake_session,
    )

    db_generator = database.get_db()

    yielded_session = next(db_generator)

    assert yielded_session is fake_session
    assert state["closed"] is False

    db_generator.close()

    assert state["closed"] is True