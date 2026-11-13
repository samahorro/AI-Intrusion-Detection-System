from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.app.ip_management import routes
from backend.app.ip_management.firewall import SimulatedFirewall


class FakeDB:
    def __init__(self):
        self.rollback_called = False
        self.commit_called = False

    def rollback(self):
        self.rollback_called = True

    def commit(self):
        self.commit_called = True


class FakeService:
    def __init__(self):
        self.db = FakeDB()
        self.record = None

    def get_record(self, ip_address):
        return self.record


def test_get_ip_service_uses_app_firewall():
    firewall = SimulatedFirewall()
    db = FakeDB()

    request = SimpleNamespace(
        app=SimpleNamespace(
            state=SimpleNamespace(
                ip_firewall=firewall,
            )
        )
    )

    service = routes.get_ip_service(
        request,
        db,
    )

    assert service.db is db
    assert service.firewall is firewall


def test_authenticated_user_rejects_missing_database_user():
    request = SimpleNamespace(
        session={
            "user_id": 999,
        }
    )

    class FakeUserDB:
        def get(self, model, user_id):
            return None

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        routes.get_authenticated_user(
            request,
            FakeUserDB(),
        )

    assert exc_info.value.status_code == 401

    assert (
        exc_info.value.detail
        == "Authentication required."
    )


def test_create_block_handles_missing_saved_record(
    monkeypatch,
):
    service = FakeService()
    user = SimpleNamespace(id=1)

    monkeypatch.setattr(
        routes,
        "block_permanently",
        lambda *args, **kwargs: SimpleNamespace(
            success=True,
        ),
    )

    payload = routes.BlockIPRequest(
        ip_address="192.0.2.10",
        reason="Missing record test",
    )

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        routes.create_block(
            payload,
            user,
            service,
        )

    assert exc_info.value.status_code == 503

    assert (
        exc_info.value.detail
        == "Unable to save simulated IP block."
    )

    assert service.db.rollback_called is True


def test_create_block_handles_value_error(
    monkeypatch,
):
    service = FakeService()
    user = SimpleNamespace(id=1)

    def raise_value_error(*args, **kwargs):
        raise ValueError(
            "Invalid block request."
        )

    monkeypatch.setattr(
        routes,
        "block_permanently",
        raise_value_error,
    )

    payload = routes.BlockIPRequest(
        ip_address="192.0.2.20",
        reason="Value error test",
    )

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        routes.create_block(
            payload,
            user,
            service,
        )

    assert exc_info.value.status_code == 400

    assert (
        exc_info.value.detail
        == "Invalid block request."
    )

    assert service.db.rollback_called is True


def test_create_block_handles_runtime_error(
    monkeypatch,
):
    service = FakeService()
    user = SimpleNamespace(id=1)

    def raise_runtime_error(*args, **kwargs):
        raise RuntimeError(
            "Simulated firewall failure."
        )

    monkeypatch.setattr(
        routes,
        "block_permanently",
        raise_runtime_error,
    )

    payload = routes.BlockIPRequest(
        ip_address="192.0.2.30",
        reason="Runtime failure test",
    )

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        routes.create_block(
            payload,
            user,
            service,
        )

    assert exc_info.value.status_code == 503

    assert (
        exc_info.value.detail
        == "Unable to save simulated IP block."
    )

    assert service.db.rollback_called is True


def test_delete_block_handles_value_error(
    monkeypatch,
):
    service = FakeService()
    user = SimpleNamespace(id=1)

    service.record = SimpleNamespace(
        created_by_user_id=1,
    )

    def raise_value_error(*args, **kwargs):
        raise ValueError(
            "Invalid unblock request."
        )

    monkeypatch.setattr(
        routes,
        "unblock_saved_ip",
        raise_value_error,
    )

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        routes.delete_block(
            "192.0.2.40",
            user,
            service,
        )

    assert exc_info.value.status_code == 400

    assert (
        exc_info.value.detail
        == "Invalid unblock request."
    )


def test_delete_block_handles_runtime_error(
    monkeypatch,
):
    service = FakeService()
    user = SimpleNamespace(id=1)

    service.record = SimpleNamespace(
        created_by_user_id=1,
    )

    def raise_runtime_error(*args, **kwargs):
        raise RuntimeError(
            "Simulated unblock failure."
        )

    monkeypatch.setattr(
        routes,
        "unblock_saved_ip",
        raise_runtime_error,
    )

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        routes.delete_block(
            "192.0.2.50",
            user,
            service,
        )

    assert exc_info.value.status_code == 503

    assert (
        exc_info.value.detail
        == "Unable to unblock IP address."
    )

    assert service.db.rollback_called is True