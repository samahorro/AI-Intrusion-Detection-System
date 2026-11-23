
import pytest
from fastapi import HTTPException

from backend.app.detection import routes

# --------------------------------------------------
# MODEL LOADING ERROR HANDLING
# --------------------------------------------------

def test_get_detection_model_handles_missing_model_file(
    monkeypatch,
):
    monkeypatch.setenv(
        "MODEL_PATH",
        "missing-model.pkl",
    )

    def raise_missing_file(path):
        raise FileNotFoundError(path)

    monkeypatch.setattr(
        routes,
        "load_model",
        raise_missing_file,
    )

    with pytest.raises(HTTPException) as exc_info:
        routes.get_detection_model()

    assert exc_info.value.status_code == 503
    assert (
        exc_info.value.detail
        == "Detection model is unavailable."
    )


# --------------------------------------------------
# NORMAL ML PREDICTION TESTS
# --------------------------------------------------

@pytest.mark.parametrize(
    "prediction",
    [
        "0",
        "false",
        "normal",
        "benign",
        " NORMAL ",
        "False",
    ],
)
def test_prediction_is_attack_rejects_normal_strings(
    prediction,
):
    assert (
        routes.prediction_is_attack(prediction)
        is False
    )


# --------------------------------------------------
# ATTACK ML PREDICTION TESTS
# --------------------------------------------------

@pytest.mark.parametrize(
    "prediction",
    [
        "1",
        "attack",
        "malicious",
        "intrusion",
        " ATTACK ",
    ],
)
def test_prediction_is_attack_accepts_attack_strings(
    prediction,
):
    assert (
        routes.prediction_is_attack(prediction)
        is True
    )


# --------------------------------------------------
# NON-STRING ML PREDICTION TESTS
# --------------------------------------------------

def test_prediction_is_attack_handles_non_strings():
    assert routes.prediction_is_attack(1) is True
    assert routes.prediction_is_attack(0) is False
    assert routes.prediction_is_attack(True) is True
    assert routes.prediction_is_attack(False) is False


# --------------------------------------------------
# UNKNOWN ML PREDICTION VALIDATION
# --------------------------------------------------

@pytest.mark.parametrize(
    "prediction",
    [
        "",
        "unknown",
        "error",
        "invalid_prediction",
    ],
)
def test_prediction_is_attack_rejects_unknown_labels(
    prediction,
):
    with pytest.raises(ValueError):
        routes.prediction_is_attack(prediction)


# --------------------------------------------------
# SIGNATURE SEVERITY CONFIDENCE TESTS
# --------------------------------------------------

@pytest.mark.parametrize(
    "severity, expected_confidence",
    [
        ("normal", 0.0),
        ("low", 0.3),
        ("medium", 0.6),
        ("high", 0.9),
    ],
)
def test_signature_severity_confidence_mapping(
    severity,
    expected_confidence,
):
    confidence = routes.severity_confidence(
        severity
    )

    assert confidence == pytest.approx(
        expected_confidence
    )


# --------------------------------------------------
# SIGNATURE SEVERITY TO THREAT SCORE TESTS
# --------------------------------------------------

@pytest.mark.parametrize(
    "severity, expected_score, expected_classification",
    [
        ("low", 30, "low"),
        ("medium", 60, "medium"),
        ("high", 90, "high"),
    ],
)
def test_signature_severity_produces_expected_threat_score(
    severity,
    expected_score,
    expected_classification,
):
    confidence = routes.severity_confidence(
        severity
    )

    result = routes.score_threat(
        detected=True,
        confidence=confidence,
        attack_type="test_signature",
    )

    assert result["detected"] is True
    assert result["threat_score"] == expected_score
    assert result["classification"] == expected_classification


# --------------------------------------------------
# NORMAL SIGNATURE RESULT TEST
# --------------------------------------------------

def test_no_signature_detection_produces_normal_score():
    confidence = routes.severity_confidence(
        "normal"
    )

    result = routes.score_threat(
        detected=False,
        confidence=confidence,
        attack_type=None,
    )

    assert result["detected"] is False
    assert result["threat_score"] == 0
    assert result["classification"] == "normal"
