from types import SimpleNamespace

import pytest

from backend.app.ip_management.firewall import (
    SimulatedFirewall,
)
from backend.app.ip_management.permanent import (
    block_permanently,
    restore_permanent_blocks,
)
from backend.app.ip_management.service import (
    IPActionResult,
    IPBlockingService,
)


class FakeQuery:
    def __init__(self, records):
        self.records = records

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def all(self):
        return self.records


class FakeDB:
    def __init__(self, records=None):
        self.records = records or []

    def query(self, model):
        return FakeQuery(self.records)


def test_block_permanently_rejects_invalid_saved_record(
    monkeypatch,
):
    db = FakeDB()
    firewall = SimulatedFirewall()

    service = IPBlockingService(
        db,
        firewall,
    )

    result = IPActionResult(
        action="block",
        ip_address="192.168.1.50",
        success=True,
        changed=True,
        status="blocked",
        record_id=1,
        message="blocked",
    )

    monkeypatch.setattr(
        service,
        "block_ip",
        lambda ip_address, reason=None: result,
    )

    monkeypatch.setattr(
        service,
        "get_record",
        lambda ip_address: None,
    )

    with pytest.raises(
        RuntimeError,
        match=(
            "Permanent block was not saved correctly"
        ),
    ):
        block_permanently(
            service,
            "192.168.1.50",
            reason="Test block",
        )


def test_restore_permanent_blocks_rejects_failed_restore(
    monkeypatch,
):
    record = SimpleNamespace(
        id=1,
        ip_address="192.168.1.60",
        status="blocked",
        block_type="permanent",
        expires_at=None,
    )

    db = FakeDB(
        records=[record],
    )

    firewall = SimulatedFirewall()

    service = IPBlockingService(
        db,
        firewall,
    )

    monkeypatch.setattr(
        firewall,
        "is_blocked",
        lambda ip_address: False,
    )

    monkeypatch.setattr(
        firewall,
        "block_ip",
        lambda ip_address: None,
    )

    with pytest.raises(
        RuntimeError,
        match=(
            "Could not restore simulated permanent block"
        ),
    ):
        restore_permanent_blocks(
            service
        )