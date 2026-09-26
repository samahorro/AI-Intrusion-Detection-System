from typing import Any, Dict


def detect_signature(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform simple signature-based intrusion detection.

    Returns a consistent result dictionary that can later be consumed
    by threat scoring and classification components.
    """

    if not isinstance(event, dict):
        return {
            "detected": False,
            "attack_type": None,
            "severity": "normal",
            "reason": "invalid_event",
        }

    # Example signature 1: repeated failed login attempts
    failed_logins = event.get("failed_login_attempts", 0)

    if isinstance(failed_logins, int) and failed_logins >= 5:
        return {
            "detected": True,
            "attack_type": "brute_force",
            "severity": "high",
            "reason": "multiple_failed_login_attempts",
        }

    # Example signature 2: port scan indicator
    ports_scanned = event.get("ports_scanned", 0)

    if isinstance(ports_scanned, int) and ports_scanned >= 20:
        return {
            "detected": True,
            "attack_type": "port_scan",
            "severity": "medium",
            "reason": "large_number_of_ports_scanned",
        }

    return {
        "detected": False,
        "attack_type": None,
        "severity": "normal",
        "reason": "no_known_signature",
    }