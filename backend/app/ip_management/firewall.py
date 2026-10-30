
"""Safe firewall abstraction for the AEGIS backend.

The simulated firewall does not change real operating-system
firewall rules. It keeps blocked IP addresses in memory.
"""

from dataclasses import dataclass
from typing import Protocol

from backend.app.ip_management.validation import validate_ip_address


@dataclass(frozen=True)
class FirewallResult:
    """Result of a firewall operation."""

    success: bool
    ip_address: str
    action: str
    message: str


class FirewallBackend(Protocol):
    """Interface for firewall implementations."""

    def block_ip(self, ip_address: str) -> FirewallResult:
        ...

    def unblock_ip(self, ip_address: str) -> FirewallResult:
        ...

    def is_blocked(self, ip_address: str) -> bool:
        ...


class SimulatedFirewall:
    """Firewall simulator for local development and testing.

    No real firewall commands are executed.
    """

    def __init__(self):
        self._blocked_ips: set[str] = set()

    def block_ip(self, ip_address: str) -> FirewallResult:
        """Simulate blocking a validated IP address."""

        validated_ip = validate_ip_address(ip_address)

        if validated_ip in self._blocked_ips:
            return FirewallResult(
                success=False,
                ip_address=validated_ip,
                action="block",
                message="IP address is already blocked.",
            )

        self._blocked_ips.add(validated_ip)

        return FirewallResult(
            success=True,
            ip_address=validated_ip,
            action="block",
            message="IP address blocked in simulation mode.",
        )

    def unblock_ip(self, ip_address: str) -> FirewallResult:
        """Simulate unblocking a validated IP address."""

        validated_ip = validate_ip_address(ip_address)

        if validated_ip not in self._blocked_ips:
            return FirewallResult(
                success=False,
                ip_address=validated_ip,
                action="unblock",
                message="IP address is not currently blocked.",
            )

        self._blocked_ips.remove(validated_ip)

        return FirewallResult(
            success=True,
            ip_address=validated_ip,
            action="unblock",
            message="IP address unblocked in simulation mode.",
        )

    def is_blocked(self, ip_address: str) -> bool:
        """Check whether an IP is blocked in this simulator."""

        validated_ip = validate_ip_address(ip_address)

        return validated_ip in self._blocked_ips

    def list_blocked_ips(self) -> list[str]:
        """Return all simulated blocked IP addresses."""

        return sorted(self._blocked_ips)
