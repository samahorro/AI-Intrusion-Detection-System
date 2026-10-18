
"""AEGIS reusable signature rule definitions.

KAN-185: Define Signature Detection Rule Structure.

This module defines configurable rule metadata and conditions.
It does not execute intrusion detection.
"""

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConditionOperator(str, Enum):
    GTE = "gte"
    GT = "gt"
    LTE = "lte"
    LT = "lt"
    EQ = "eq"


@dataclass(frozen=True)
class RuleCondition:
    field_name: str
    operator: ConditionOperator
    value: int | float

    def __post_init__(self):
        if not self.field_name.strip():
            raise ValueError("Condition field name cannot be empty")

        if not isinstance(self.operator, ConditionOperator):
            raise ValueError("Invalid condition operator")

        if isinstance(self.value, bool) or not isinstance(
            self.value, (int, float)
        ):
            raise ValueError("Condition value must be numeric")


@dataclass(frozen=True)
class SignatureRule:
    rule_id: str
    name: str
    description: str
    attack_type: str
    severity: Severity
    conditions: tuple[RuleCondition, ...]
    enabled: bool = True
    window_seconds: int | None = None

    def __post_init__(self):
        if not self.rule_id.strip():
            raise ValueError("Rule ID cannot be empty")

        if not self.name.strip():
            raise ValueError("Rule name cannot be empty")

        if not self.attack_type.strip():
            raise ValueError("Attack type cannot be empty")

        if not isinstance(self.severity, Severity):
            raise ValueError("Invalid severity")

        if not self.conditions:
            raise ValueError("At least one condition is required")

        if self.window_seconds is not None and (
            isinstance(self.window_seconds, bool)
            or not isinstance(self.window_seconds, int)
            or self.window_seconds <= 0
        ):
            raise ValueError("Time window must be positive")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


BRUTE_FORCE_RULE = SignatureRule(
    rule_id="AEGIS-SIG-001",
    name="Multiple Failed Login Attempts",
    description="Detects repeated failed authentication attempts.",
    attack_type="brute_force",
    severity=Severity.HIGH,
    conditions=(
        RuleCondition(
            field_name="failed_login_attempts",
            operator=ConditionOperator.GTE,
            value=5,
        ),
    ),
)


PORT_SCAN_RULE = SignatureRule(
    rule_id="AEGIS-SIG-002",
    name="Multiple Destination Ports Scanned",
    description="Detects a high number of destination ports scanned.",
    attack_type="port_scan",
    severity=Severity.MEDIUM,
    conditions=(
        RuleCondition(
            field_name="ports_scanned",
            operator=ConditionOperator.GTE,
            value=20,
        ),
    ),
)


DEFAULT_SIGNATURE_RULES = (
    BRUTE_FORCE_RULE,
    PORT_SCAN_RULE,
)
