from ml.detection.signature_detection import detect_signature


def test_brute_force_signature_is_detected():
    event = {
        "failed_login_attempts": 8,
        "ports_scanned": 2,
    }

    result = detect_signature(event)

    assert result["detected"] is True
    assert result["attack_type"] == "brute_force"
    assert result["severity"] == "high"


def test_port_scan_signature_is_detected():
    event = {
        "failed_login_attempts": 0,
        "ports_scanned": 30,
    }

    result = detect_signature(event)

    assert result["detected"] is True
    assert result["attack_type"] == "port_scan"
    assert result["severity"] == "medium"


def test_normal_traffic_is_not_detected():
    event = {
        "failed_login_attempts": 1,
        "ports_scanned": 3,
    }

    result = detect_signature(event)

    assert result["detected"] is False
    assert result["attack_type"] is None
    assert result["severity"] == "normal"


def test_invalid_input_is_handled():
    result = detect_signature(None)

    assert result["detected"] is False
    assert result["attack_type"] is None
    assert result["severity"] == "normal"


def test_result_contains_expected_fields():
    event = {
        "failed_login_attempts": 0,
        "ports_scanned": 0,
    }

    result = detect_signature(event)

    assert "detected" in result
    assert "attack_type" in result
    assert "severity" in result
    assert "reason" in result