from dataclasses import dataclass

from sqlalchemy.orm import Session

from .firewall import SimulatedFirewall
from .validation import validate_ip_address
from ..models.blocked_ip import BlockedIP


@dataclass(frozen=True)
class IPActionResult:
    action: str
    ip_address: str
    success: bool
    changed: bool
    status: str
    record_id: int | None
    message: str
    simulated: bool = True


class IPBlockingService:
    """Coordinate saved IP records with a simulated firewall."""

    def __init__(
        self,
        db: Session,
        firewall: SimulatedFirewall,
    ) -> None:
        if not isinstance(firewall, SimulatedFirewall):
            raise TypeError("Sprint 4 supports SimulatedFirewall only.")

        self.db = db
        self.firewall = firewall

    def get_record(self, ip_address: str) -> BlockedIP | None:
        normalized = validate_ip_address(ip_address)

        return (
            self.db.query(BlockedIP)
            .filter(BlockedIP.ip_address == normalized)
            .first()
        )

    def block_ip(
        self,
        ip_address: str,
        *,
        reason: str | None = None,
    ) -> IPActionResult:
        """Save a blocked IP and update the simulated firewall."""

        normalized = validate_ip_address(ip_address)

        if reason is not None:
            if not isinstance(reason, str) or len(reason) > 255:
                raise ValueError(
                    "Block reason must be text of 255 characters or fewer."
                )

        record = self.get_record(normalized)

        was_blocked = (
            record is not None and record.status == "blocked"
        )

        if record is None:
            record = BlockedIP(
                ip_address=normalized,
                block_type="permanent",
                status="blocked",
                reason=reason,
                expires_at=None,
            )
            self.db.add(record)
        else:
            record.status = "blocked"
            record.block_type = "permanent"
            record.expires_at = None

            if reason is not None:
                record.reason = reason

        was_simulated_blocked = self.firewall.is_blocked(normalized)
        simulation_changed = False

        try:
            self.db.flush()

            self.firewall.block_ip(normalized)

            simulation_changed = (
                not was_simulated_blocked
                and self.firewall.is_blocked(normalized)
            )

            if not self.firewall.is_blocked(normalized):
                raise RuntimeError(
                    "Simulated firewall could not block the IP."
                )

            self.db.commit()
            self.db.refresh(record)

        except Exception:
            self.db.rollback()

            if simulation_changed:
                self.firewall.unblock_ip(normalized)

            raise

        return IPActionResult(
            action="block",
            ip_address=normalized,
            success=True,
            changed=not was_blocked or simulation_changed,
            status="blocked",
            record_id=record.id,
            message=(
                "IP block saved and simulated "
                "(no real firewall changes)."
            ),
        )

    def unblock_ip(self, ip_address: str) -> IPActionResult:
        """Mark a saved IP as unblocked and update the simulator."""

        normalized = validate_ip_address(ip_address)
        record = self.get_record(normalized)

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

        database_changed = record.status == "blocked"
        simulator_blocked = self.firewall.is_blocked(normalized)
        simulation_changed = False

        try:
            record.status = "unblocked"
            self.db.flush()

            if simulator_blocked:
                self.firewall.unblock_ip(normalized)

                simulation_changed = (
                    not self.firewall.is_blocked(normalized)
                )

                if not simulation_changed:
                    raise RuntimeError(
                        "Simulated firewall could not unblock the IP."
                    )

            self.db.commit()
            self.db.refresh(record)

        except Exception:
            self.db.rollback()

            if simulation_changed:
                self.firewall.block_ip(normalized)

            raise

        return IPActionResult(
            action="unblock",
            ip_address=normalized,
            success=True,
            changed=database_changed or simulation_changed,
            status="unblocked",
            record_id=record.id,
            message="Saved IP block removed from simulation.",
        )
