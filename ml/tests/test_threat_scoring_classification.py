
import pytest

from ml.scoring.threat_scoring import (
    VALID_CLASSIFICATIONS,
    classify_score,
    combine_detection_confidence,
    score_threat,
    validate_confidence,
)


# --------------------------------------------------
# NORMAL TRAFFIC CLASSIFICATION
# --------------------------------------------------

def test_normal_traffic_receives_normal_classification():
    result = score_threat(
        detected=False,
        confidence=0.0,
        attack_type=None,
    )

    assert result["threat_score"] == 0
    assert result["classification"] == "normal"


# --------------------------------------------------
# LOW THREAT CLASSIFICATION
# --------------------------------------------------

def test_low_threat_classification():
    result = score_threat(
        detected=True,
        confidence=0.20,
        attack_type="suspicious_activity",
    )

    assert result["threat_score"] == 20
    assert result["classification"] == "low"


# --------------------------------------------------
# MEDIUM THREAT CLASSIFICATION
# --------------------------------------------------

def test_medium_threat_classification():
    result = score_threat(
        detected=True,
        confidence=0.55,
        attack_type="port_scan",
    )

    assert result["threat_score"] == 55
    assert result["classification"] == "medium"


# --------------------------------------------------
# HIGH THREAT CLASSIFICATION
# --------------------------------------------------

def test_high_threat_classification():
    result = score_threat(
        detected=True,
        confidence=0.90,
        attack_type="brute_force",
    )

    assert result["threat_score"] == 90
    assert result["classification"] == "high"


# --------------------------------------------------
# VALID CLASSIFICATION VALUES
# --------------------------------------------------

def test_classifications_are_recognized_values():
    for score in [0, 20, 55, 90]:
        classification = classify_score(score)

        assert classification in VALID_CLASSIFICATIONS


# --------------------------------------------------
# CONFIDENCE INPUT VALIDATION
# --------------------------------------------------

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


# --------------------------------------------------
# INVALID THREAT SCORE
# --------------------------------------------------

def test_invalid_score_raises_error():
    with pytest.raises(ValueError):
        classify_score(101)


# --------------------------------------------------
# REQUIRED OUTPUT FIELDS
# --------------------------------------------------

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


# --------------------------------------------------
# THREAT CLASSIFICATION BOUNDARY TESTS
# --------------------------------------------------

@pytest.mark.parametrize(
    "score, expected_classification",
    [
        (0, "normal"),
        (1, "low"),
        (39, "low"),
        (40, "medium"),
        (69, "medium"),
        (70, "high"),
        (100, "high"),
    ],
)
def test_threat_classification_boundaries(
    score,
    expected_classification,
):
    assert classify_score(score) == expected_classification


# --------------------------------------------------
# INVALID THREAT SCORE INPUT TESTS
# --------------------------------------------------

@pytest.mark.parametrize(
    "invalid_score",
    [
        -1,
        101,
        50.5,
        "high",
        None,
    ],
)
def test_invalid_threat_scores(invalid_score):
    expected_error = (
        TypeError
        if not isinstance(invalid_score, int)
        else ValueError
    )

    with pytest.raises(expected_error):
        classify_score(invalid_score)


# --------------------------------------------------
# SPRINT 5 TASK 6 - NON-FINITE CONFIDENCE TESTS
# --------------------------------------------------

@pytest.mark.parametrize(
    "invalid_confidence",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_nonfinite_confidence_raises_error(
    invalid_confidence,
):
    with pytest.raises(ValueError):
        score_threat(
            detected=True,
            confidence=invalid_confidence,
            attack_type="test_attack",
        )


# --------------------------------------------------
# BOOLEAN CONFIDENCE VALIDATION
# --------------------------------------------------

@pytest.mark.parametrize(
    "invalid_confidence",
    [
        True,
        False,
    ],
)
def test_boolean_confidence_raises_error(
    invalid_confidence,
):
    with pytest.raises(TypeError):
        score_threat(
            detected=True,
            confidence=invalid_confidence,
            attack_type="test_attack",
        )


# --------------------------------------------------
# BOOLEAN SCORE VALIDATION
# --------------------------------------------------

@pytest.mark.parametrize(
    "invalid_score",
    [
        True,
        False,
    ],
)
def test_boolean_score_raises_error(invalid_score):
    with pytest.raises(TypeError):
        classify_score(invalid_score)


# --------------------------------------------------
# VALID CONFIDENCE INPUT
# --------------------------------------------------

def test_validate_confidence_accepts_valid_value():
    assert validate_confidence(0.85) == pytest.approx(0.85)


# --------------------------------------------------
# COMBINED ML AND SIGNATURE CONFIDENCE TESTS
# --------------------------------------------------

@pytest.mark.parametrize(
    "ml_detected, ml_confidence, signature_detected, "
    "signature_confidence, expected",
    [
        (True, 0.85, True, 0.60, 0.85),
        (True, 0.75, True, 0.90, 0.90),
        (True, 0.65, False, 0.0, 0.65),
        (False, 0.0, True, 0.60, 0.60),
        (False, 0.0, False, 0.0, 0.0),
    ],
)
def test_combined_detection_confidence(
    ml_detected,
    ml_confidence,
    signature_detected,
    signature_confidence,
    expected,
):
    result = combine_detection_confidence(
        ml_detected=ml_detected,
        ml_confidence=ml_confidence,
        signature_detected=signature_detected,
        signature_confidence=signature_confidence,
    )

    assert result == pytest.approx(expected)


# --------------------------------------------------
# INACTIVE DETECTION SHOULD NOT CONTRIBUTE
# --------------------------------------------------

def test_inactive_detection_does_not_contribute():
    result = combine_detection_confidence(
        ml_detected=False,
        ml_confidence=0.95,
        signature_detected=True,
        signature_confidence=0.60,
    )

    assert result == pytest.approx(0.60)


# --------------------------------------------------
# INVALID COMBINED CONFIDENCE
# --------------------------------------------------

@pytest.mark.parametrize(
    "invalid_confidence",
    [
        float("nan"),
        float("inf"),
        -0.1,
        1.1,
    ],
)
def test_combination_rejects_invalid_confidence(
    invalid_confidence,
):
    with pytest.raises(ValueError):
        combine_detection_confidence(
            ml_detected=True,
            ml_confidence=invalid_confidence,
            signature_detected=False,
            signature_confidence=0.0,
        )


# --------------------------------------------------
# INVALID DETECTION FLAG
# --------------------------------------------------

def test_combination_rejects_invalid_detection_flag():
    with pytest.raises(TypeError):
        combine_detection_confidence(
            ml_detected=1,
            ml_confidence=0.8,
            signature_detected=False,
            signature_confidence=0.0,
        )
