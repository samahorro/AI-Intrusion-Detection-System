
import math
from typing import Any, Dict, Optional


VALID_CLASSIFICATIONS = {
    "normal",
    "low",
    "medium",
    "high",
}


# --------------------------------------------------
# VALIDATE SCORING CONFIDENCE
# --------------------------------------------------

def validate_confidence(confidence: float) -> float:
    """
    Validate and normalize scoring confidence.

    Confidence must be:
    - Numeric, excluding booleans
    - Finite (not NaN or infinity)
    - Between 0.0 and 1.0
    """

    if isinstance(confidence, bool) or not isinstance(
        confidence, (int, float)
    ):
        raise TypeError("confidence must be numeric")

    confidence = float(confidence)

    if not math.isfinite(confidence):
        raise ValueError("confidence must be finite")

    if not 0.0 <= confidence <= 1.0:
        raise ValueError(
            "confidence must be between 0.0 and 1.0"
        )

    return confidence


# --------------------------------------------------
# CLASSIFY THREAT SCORE
# --------------------------------------------------

def classify_score(score: int) -> str:
    """
    Convert a threat score from 0-100 into a classification.
    """

    if isinstance(score, bool) or not isinstance(score, int):
        raise TypeError("score must be an integer")

    if score < 0 or score > 100:
        raise ValueError("score must be between 0 and 100")

    if score == 0:
        return "normal"

    if score < 40:
        return "low"

    if score < 70:
        return "medium"

    return "high"


# --------------------------------------------------
# COMBINE ML AND SIGNATURE CONFIDENCE
# --------------------------------------------------

def combine_detection_confidence(
    ml_detected: bool,
    ml_confidence: float,
    signature_detected: bool,
    signature_confidence: float,
) -> float:
    """
    Combine ML and signature evidence using the
    maximum-evidence scoring policy.

    Only active detection sources contribute to the
    final confidence.

    This does not add probabilities together or
    assume the detection sources are independent.
    """

    if not isinstance(ml_detected, bool):
        raise TypeError("ml_detected must be a boolean")

    if not isinstance(signature_detected, bool):
        raise TypeError("signature_detected must be a boolean")

    ml_confidence = validate_confidence(ml_confidence)

    signature_confidence = validate_confidence(
        signature_confidence
    )

    active_ml_confidence = (
        ml_confidence if ml_detected else 0.0
    )

    active_signature_confidence = (
        signature_confidence if signature_detected else 0.0
    )

    return max(
        active_ml_confidence,
        active_signature_confidence,
    )


# --------------------------------------------------
# PRODUCE FINAL THREAT SCORE
# --------------------------------------------------

def score_threat(
    detected: bool,
    confidence: float = 0.0,
    attack_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Produce a normalized threat score and classification.

    When detected is False, the threat score is 0.

    When detected is True, scoring confidence is
    converted to a score from 1 to 100.

    Existing response fields are preserved.
    """

    if not isinstance(detected, bool):
        raise TypeError("detected must be a boolean")

    confidence = validate_confidence(confidence)

    if not detected:
        score = 0
    else:
        score = max(
            1,
            round(confidence * 100),
        )

    classification = classify_score(score)

    return {
        "detected": detected,
        "attack_type": attack_type,
        "threat_score": score,
        "classification": classification,
    }
