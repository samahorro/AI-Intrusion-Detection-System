import pytest

from ml.scoring.threat_scoring import (
    VALID_CLASSIFICATIONS,
    classify_score,
    score_threat,
)


def test_normal_traffic_receives_normal_classification():
    result = score_threat(
        detected=False,
        confidence=0.0,
        attack_type=None,
    )

    assert result["threat_score"] == 0
    assert result["classification"] == "normal"


def test_low_threat_classification():
    result = score_threat(
        detected=True,
        confidence=0.20,
        attack_type="suspicious_activity",
    )

    assert result["threat_score"] == 20
    assert result["classification"] == "low"


def test_medium_threat_classification():
    result = score_threat(
        detected=True,
        confidence=0.55,
        attack_type="port_scan",
    )

    assert result["threat_score"] == 55
    assert result["classification"] == "medium"


def test_high_threat_classification():
    result = score_threat(
        detected=True,
        confidence=0.90,
        attack_type="brute_force",
    )

    assert result["threat_score"] == 90
    assert result["classification"] == "high"


def test_classifications_are_recognized_values():
    for score in [0, 20, 55, 90]:
        classification = classify_score(score)
        assert classification in VALID_CLASSIFICATIONS


def test_invalid_confidence_below_zero_raises_error():
    with pytest.raises(ValueError):
        score_threat(
            detected=True,
            confidence=-0.1,
            attack_type="port_scan",
        )


def test_invalid_confidence_above_one_raises_error():
    with pytest.raises(ValueError):
        score_threat(
            detected=True,
            confidence=1.1,
            attack_type="port_scan",
        )


def test_invalid_score_raises_error():
    with pytest.raises(ValueError):
        classify_score(101)


def test_output_contains_expected_fields():
    result = score_threat(
        detected=True,
        confidence=0.75,
        attack_type="brute_force",
    )

    assert "detected" in result
    assert "attack_type" in result
    assert "threat_score" in result
    assert "classification" in result