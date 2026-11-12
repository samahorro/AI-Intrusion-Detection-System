from types import SimpleNamespace

import pytest

from backend.app.ip_management.firewall import (
    SimulatedFirewall,
)
from backend.app.ip_management.service import (
    IPActionResult,
    IPBlockingService,
)
from backend.app.ip_management.unblocking import (
    unblock_saved_ip,
)


class FakeDB:
    pass


def test_unblock_saved_ip_rejects_unverified_result(
    monkeypatch,
):
    firewall = SimulatedFirewall()
    service = IPBlockingService(
        FakeDB(),
        firewall,
    )

    original_record = SimpleNamespace(
        id=1,
        ip_address="192.168.1.80",
        status="blocked",
    )

    saved_record = SimpleNamespace(
        id=1,
        ip_address="192.168.1.80",
        status="blocked",
    )

    records = iter(
        [
            original_record,
            saved_record,
        ]
    )

    monkeypatch.setattr(
        service,
        "get_record",
        lambda ip_address: next(records),
    )

    monkeypatch.setattr(
        service,
        "unblock_ip",
        lambda ip_address: IPActionResult(
            action="unblock",
            ip_address=ip_address,
            success=True,
            changed=True,
            status="unblocked",
            record_id=1,
            message="unblocked",
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="IP unblocking could not be verified",
    ):
        unblock_saved_ip(
            service,
            "192.168.1.80",
        )