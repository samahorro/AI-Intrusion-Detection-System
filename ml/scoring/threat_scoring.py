from typing import Any, Dict, Optional


VALID_CLASSIFICATIONS = {
    "normal",
    "low",
    "medium",
    "high",
}


def classify_score(score: int) -> str:
    """
    Convert a threat score from 0-100 into a classification.
    """

    if not isinstance(score, int):
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


def score_threat(
    detected: bool,
    confidence: float = 0.0,
    attack_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Produce a normalized threat score and classification.
    confidence must be between 0.0 and 1.0.
    """

    if not isinstance(detected, bool):
        raise TypeError("detected must be a boolean")

    if not isinstance(confidence, (int, float)):
        raise TypeError("confidence must be numeric")

    confidence = float(confidence)

    if confidence < 0.0 or confidence > 1.0:
        raise ValueError("confidence must be between 0.0 and 1.0")

    if not detected:
        score = 0
    else:
        score = max(1, round(confidence * 100))

    classification = classify_score(score)

    return {
        "detected": detected,
        "attack_type": attack_type,
        "threat_score": score,
        "classification": classification,
    }