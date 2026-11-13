from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from backend.app.auth import routes


class FakeQuery:
    def __init__(self, result=None):
        self.result = result

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.result


class FakeDB:
    def __init__(
        self,
        query_result=None,
        commit_error=None,
    ):
        self.query_result = query_result
        self.commit_error = commit_error

        self.add_called = False
        self.commit_called = False
        self.refresh_called = False
        self.rollback_called = False

    def query(self, model):
        return FakeQuery(
            self.query_result
        )

    def add(self, user):
        self.add_called = True

    def commit(self):
        self.commit_called = True

        if self.commit_error is not None:
            raise self.commit_error

    def refresh(self, user):
        self.refresh_called = True

    def rollback(self):
        self.rollback_called = True


def test_register_rejects_invalid_username():
    db = FakeDB()

    data = routes.RegisterRequest(
        username="!!",
        password="ValidPassword123!",
    )

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        routes.register(
            data,
            db,
        )

    assert exc_info.value.status_code == 400

    assert (
        exc_info.value.detail
        == "Username must be at least 3 characters."
    )

    assert db.add_called is False
    assert db.commit_called is False


def test_register_rolls_back_on_integrity_error(
    monkeypatch,
):
    integrity_error = IntegrityError(
        "INSERT INTO users",
        {},
        Exception("duplicate username"),
    )

    db = FakeDB(
        query_result=None,
        commit_error=integrity_error,
    )

    monkeypatch.setattr(
        routes,
        "hash_password",
        lambda password: "hashed-password",
    )

    data = routes.RegisterRequest(
        username="newuser",
        password="ValidPassword123!",
    )

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        routes.register(
            data,
            db,
        )

    assert exc_info.value.status_code == 409

    assert (
        exc_info.value.detail
        == "Username already exists."
    )

    assert db.add_called is True
    assert db.commit_called is True
    assert db.rollback_called is True
    assert db.refresh_called is False


def test_login_rejects_already_locked_account(
    monkeypatch,
):
    user = SimpleNamespace(
        id=1,
        username="lockeduser",
        password_hash="hashed-password",
    )

    db = FakeDB(
        query_result=user,
    )

    request = SimpleNamespace(
        session={}
    )

    data = routes.LoginRequest(
        username="lockeduser",
        password="ValidPassword123!",
    )

    attempts = []

    monkeypatch.setattr(
        routes,
        "is_account_locked",
        lambda db, username: True,
    )

    monkeypatch.setattr(
        routes,
        "record_login_attempt",
        lambda db, **kwargs: attempts.append(
            kwargs
        ),
    )

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        routes.login(
            data,
            request,
            db,
        )

    assert exc_info.value.status_code == 423

    assert (
        exc_info.value.detail
        == (
            "Account temporarily locked due to "
            "too many failed login attempts."
        )
    )

    assert attempts == [
        {
            "username": "lockeduser",
            "success": False,
            "reason": "account_locked",
        }
    ]


def test_login_bad_password_can_immediately_lock_account(
    monkeypatch,
):
    user = SimpleNamespace(
        id=1,
        username="lockeduser",
        password_hash="hashed-password",
    )

    db = FakeDB(
        query_result=user,
    )

    request = SimpleNamespace(
        session={}
    )

    data = routes.LoginRequest(
        username="lockeduser",
        password="WrongPassword123!",
    )

    lock_checks = iter(
        [False, True]
    )

    monkeypatch.setattr(
        routes,
        "is_account_locked",
        lambda db, username: next(lock_checks),
    )

    monkeypatch.setattr(
        routes,
        "verify_password",
        lambda plain, hashed: False,
    )

    monkeypatch.setattr(
        routes,
        "record_login_attempt",
        lambda *args, **kwargs: None,
    )

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        routes.login(
            data,
            request,
            db,
        )

    assert exc_info.value.status_code == 423

    assert (
        exc_info.value.detail
        == (
            "Account temporarily locked due to "
            "too many failed login attempts."
        )
    )


def test_get_current_user_rejects_missing_session():
    request = SimpleNamespace(
        session={}
    )

    db = FakeDB()

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        routes.get_current_user(
            request,
            db,
        )

    assert exc_info.value.status_code == 401

    assert (
        exc_info.value.detail
        == "Authentication required."
    )


def test_get_current_user_clears_stale_session():
    request = SimpleNamespace(
        session={
            "user_id": 999,
            "username": "missinguser",
        }
    )

    db = FakeDB(
        query_result=None,
    )

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        routes.get_current_user(
            request,
            db,
        )

    assert exc_info.value.status_code == 401

    assert (
        exc_info.value.detail
        == "Authentication required."
    )

    assert request.session == {}