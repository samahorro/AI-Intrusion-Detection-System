
"""KAN-229: verified, idempotent IP unblocking in simulation mode.

This module does not execute operating-system firewall commands.
KAN-227 handles database transactions and rollback.
"""

from .service import IPActionResult, IPBlockingService
from .validation import validate_ip_address


def unblock_saved_ip(
    service: IPBlockingService,
    ip_address: str,
) -> IPActionResult:
    """Unblock an IP and verify the database and simulated firewall.

    Unknown addresses return not_found.
    Repeated unblocking does not create new changes.
    Stale simulated firewall entries are also cleared.
    """

    if not isinstance(service, IPBlockingService):
        raise TypeError(
            "service must be an IPBlockingService instance."
        )

    normalized = validate_ip_address(ip_address)
    record = service.get_record(normalized)

    if record is None:
        return IPActionResult(
            action="unblock",
            ip_address=normalized,
            success=False,
            changed=False,
            status="not_found",
            record_id=None,
            message="No saved block exists for this IP.",
        )

    if (
        record.status == "unblocked"
        and not service.firewall.is_blocked(normalized)
    ):
        return IPActionResult(
            action="unblock",
            ip_address=normalized,
            success=True,
            changed=False,
            status="unblocked",
            record_id=record.id,
            message="IP is already unblocked; no changes needed.",
        )

    result = service.unblock_ip(normalized)

    saved = service.get_record(normalized)

    if (
        not result.success
        or saved is None
        or saved.status != "unblocked"
        or service.firewall.is_blocked(normalized)
    ):
        raise RuntimeError(
            "IP unblocking could not be verified."
        )

    return result
