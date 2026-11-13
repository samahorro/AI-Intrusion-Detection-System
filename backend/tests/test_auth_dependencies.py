from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.app.auth.dependencies import (
    require_authenticated_user,
)


class FakeQuery:
    def __init__(self, user):
        self.user = user

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.user


class FakeDB:
    def __init__(self, user):
        self.user = user

    def query(self, model):
        return FakeQuery(self.user)


def test_require_authenticated_user_rejects_missing_session():
    request = SimpleNamespace(
        session={},
    )

    db = FakeDB(
        user=None,
    )

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        require_authenticated_user(
            request,
            db,
        )

    assert exc_info.value.status_code == 401
    assert (
        exc_info.value.detail
        == "Authentication required."
    )


def test_require_authenticated_user_clears_stale_session():
    request = SimpleNamespace(
        session={
            "user_id": 999,
            "other_data": "test",
        },
    )

    db = FakeDB(
        user=None,
    )

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        require_authenticated_user(
            request,
            db,
        )

    assert exc_info.value.status_code == 401

    assert (
        exc_info.value.detail
        == "Authentication required."
    )

    assert request.session == {}


def test_require_authenticated_user_returns_existing_user():
    user = SimpleNamespace(
        id=1,
        username="testuser",
    )

    request = SimpleNamespace(
        session={
            "user_id": 1,
        },
    )

    db = FakeDB(
        user=user,
    )

    result = require_authenticated_user(
        request,
        db,
    )

    assert result is user
    assert result.id == 1
    assert result.username == "testuser"

    assert request.session == {
        "user_id": 1,
    }