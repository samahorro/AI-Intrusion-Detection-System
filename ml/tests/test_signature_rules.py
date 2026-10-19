
"""Tests for KAN-185 signature rule definitions."""

import pytest

from ml.detection.signature_rules import (
    BRUTE_FORCE_RULE,
    DEFAULT_SIGNATURE_RULES,
    PORT_SCAN_RULE,
    ConditionOperator,
    RuleCondition,
    Severity,
    SignatureRule,
)


def test_default_rules_exist():
    assert len(DEFAULT_SIGNATURE_RULES) == 2


def test_brute_force_rule():
    assert BRUTE_FORCE_RULE.attack_type == "brute_force"
    assert BRUTE_FORCE_RULE.severity == Severity.HIGH
    assert BRUTE_FORCE_RULE.conditions[0].value == 5


def test_port_scan_rule():
    assert PORT_SCAN_RULE.attack_type == "port_scan"
    assert PORT_SCAN_RULE.severity == Severity.MEDIUM
    assert PORT_SCAN_RULE.conditions[0].value == 20


def test_rule_serialization():
    result = PORT_SCAN_RULE.to_dict()

    assert result["rule_id"] == "AEGIS-SIG-002"
    assert result["severity"] == "medium"
    assert result["conditions"][0]["operator"] == "gte"


def test_invalid_condition_field():
    with pytest.raises(ValueError):
        RuleCondition(
            field_name="",
            operator=ConditionOperator.GTE,
            value=5,
        )


def test_invalid_time_window():
    with pytest.raises(ValueError):
        SignatureRule(
            rule_id="TEST-001",
            name="Test Rule",
            description="Testing invalid time window",
            attack_type="port_scan",
            severity=Severity.LOW,
            conditions=(
                RuleCondition(
                    field_name="ports_scanned",
                    operator=ConditionOperator.GTE,
                    value=5,
                ),
            ),
            window_seconds=-1,
        )
