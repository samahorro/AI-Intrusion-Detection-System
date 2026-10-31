from ..models.blocked_ip import BlockedIP
from .service import IPActionResult, IPBlockingService
from .validation import validate_ip_address


def block_permanently(
    service: IPBlockingService,
    ip_address: str,
    *,
    reason: str | None = None,
) -> IPActionResult:
    """Save a permanent block; repeated requests reuse the same DB record."""
    if not isinstance(service, IPBlockingService):
        raise TypeError("service must be an IPBlockingService instance.")

    normalized_ip = validate_ip_address(ip_address)

    if reason is not None:
        if not isinstance(reason, str):
            raise ValueError("Reason must be text.")

        reason = reason.strip()

        if not reason:
            raise ValueError("Reason cannot be blank.")

        if len(reason) > 255:
            raise ValueError("Reason must be 255 characters or fewer.")

    # KAN-227 handles database transactions and firewall simulation.
    result = service.block_ip(normalized_ip, reason=reason)

    record = service.get_record(normalized_ip)

    if (
        record is None
        or record.status != "blocked"
        or record.block_type != "permanent"
        or record.expires_at is not None
    ):
        raise RuntimeError("Permanent block was not saved correctly.")

    return result


def restore_permanent_blocks(
    service: IPBlockingService,
) -> tuple[str, ...]:
    """Restore saved permanent blocks into an in-memory simulator.

    This does not run operating-system firewall commands.
    Returns addresses newly added to this simulator instance.
    """
    if not isinstance(service, IPBlockingService):
        raise TypeError("service must be an IPBlockingService instance.")

    records = (
        service.db.query(BlockedIP)
        .filter(
            BlockedIP.status == "blocked",
            BlockedIP.block_type == "permanent",
            BlockedIP.expires_at.is_(None),
        )
        .order_by(BlockedIP.id)
        .all()
    )

    restored = []

    for record in records:
        normalized_ip = validate_ip_address(record.ip_address)

        if service.firewall.is_blocked(normalized_ip):
            continue

        service.firewall.block_ip(normalized_ip)

        if not service.firewall.is_blocked(normalized_ip):
            raise RuntimeError(
                "Could not restore simulated permanent block."
            )

        restored.append(normalized_ip)

    return tuple(restored)
