
import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ml.detection.signature_detection import detect_signature
from ml.models.inference import load_model, run_inference
from ml.preprocessing.flow_preprocessor import preprocess_flow
from ml.scoring.threat_scoring import (
    combine_detection_confidence,
    score_threat,
)

from ..auth.dependencies import require_authenticated_user

# --------------------------------------------------
# DETECTION API ROUTER
# --------------------------------------------------

router = APIRouter(
    prefix="/detection",
    tags=["detection"],
    dependencies=[
        Depends(require_authenticated_user),
    ],
)


# --------------------------------------------------
# REQUEST MODEL
# --------------------------------------------------

class DetectionRequest(BaseModel):
    flow: dict[str, Any]
    event: dict[str, Any] = Field(default_factory=dict)


# --------------------------------------------------
# LOAD CONFIGURED ML MODEL
# --------------------------------------------------

def get_detection_model():
    """Load the configured ML model."""

    model_path = os.getenv("MODEL_PATH")

    if not model_path:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Detection model is not configured.",
        )

    try:
        return load_model(model_path)

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Detection model is unavailable.",
        ) from exc


# --------------------------------------------------
# NORMALIZE ML PREDICTION
# --------------------------------------------------

def prediction_is_attack(prediction: Any) -> bool:
    """
    Normalize recognized binary predictions.

    Reject unknown labels rather than treating them
    as confirmed attacks.
    """

    if isinstance(prediction, str):
        normalized = prediction.strip().lower()

        if normalized in {
            "0",
            "false",
            "normal",
            "benign",
        }:
            return False

        if normalized in {
            "1",
            "true",
            "attack",
            "malicious",
            "intrusion",
        }:
            return True

        raise ValueError(
            f"Unrecognized model prediction: {prediction!r}"
        )

    if isinstance(prediction, bool):
        return prediction

    if isinstance(prediction, int) and prediction in (0, 1):
        return bool(prediction)

    raise ValueError(
        f"Unsupported model prediction: {prediction!r}"
    )


# --------------------------------------------------
# SIGNATURE SEVERITY MAPPING
# --------------------------------------------------

def severity_confidence(severity: str) -> float:
    """
    Convert signature severity into scoring confidence.
    """

    confidence_map = {
        "normal": 0.0,
        "low": 0.3,
        "medium": 0.6,
        "high": 0.9,
    }

    return confidence_map.get(severity, 0.0)


# --------------------------------------------------
# DETECTION AND THREAT SCORING ENDPOINT
# --------------------------------------------------

@router.post("/analyze")
def analyze_network_flow(
    data: DetectionRequest,
    model: Any = Depends(get_detection_model),
):
    """
    Run preprocessing, ML inference, signature detection,
    and combined threat scoring.

    The final score uses the stronger available evidence
    from either ML inference or signature detection.

    Invalid inputs are handled with HTTP 400 responses.

    Existing API response fields are preserved.
    """

    # -----------------------------------------------
    # STEP 1 - PREPROCESS AND DETECT
    # -----------------------------------------------

    try:
        features = preprocess_flow(data.flow)

        inference_result = run_inference(
            model,
            features,
        )

        signature_result = detect_signature(
            data.event
        )

    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    # -----------------------------------------------
    # STEP 2 - VALIDATE AND SCORE DETECTION RESULTS
    # -----------------------------------------------

    try:
        # -------------------------------------------
        # DETERMINE DETECTION STATUS
        # -------------------------------------------

        model_detected = prediction_is_attack(
            inference_result["prediction"]
        )

        signature_detected = signature_result["detected"]

        detected = model_detected or signature_detected

        # -------------------------------------------
        # CALCULATE ML CONFIDENCE
        # -------------------------------------------

        if model_detected:
            # Use probability when available.
            # Preserve the fallback for models
            # without predict_proba().
            ml_confidence = inference_result.get(
                "attack_probability",
                1.0,
            )
        else:
            ml_confidence = 0.0

        # -------------------------------------------
        # CALCULATE SIGNATURE CONFIDENCE
        # -------------------------------------------

        if signature_detected:
            signature_confidence = severity_confidence(
                signature_result["severity"]
            )
        else:
            signature_confidence = 0.0

        # -------------------------------------------
        # COMBINE DETECTION EVIDENCE
        # -------------------------------------------

        confidence = combine_detection_confidence(
            ml_detected=model_detected,
            ml_confidence=ml_confidence,
            signature_detected=signature_detected,
            signature_confidence=signature_confidence,
        )

        # -------------------------------------------
        # IDENTIFY ATTACK TYPE
        # -------------------------------------------

        if signature_detected:
            attack_type = signature_result["attack_type"]

        elif model_detected:
            attack_type = "ml_detected"

        else:
            attack_type = None

        # -------------------------------------------
        # PRODUCE FINAL THREAT SCORE
        # -------------------------------------------

        threat_result = score_threat(
            detected=detected,
            confidence=confidence,
            attack_type=attack_type,
        )

    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    # -----------------------------------------------
    # STEP 3 - RETURN DETECTION RESULTS
    # -----------------------------------------------

    return {
        "status": "success",
        "features": features,
        "inference": inference_result,
        "signature": signature_result,
        "threat": threat_result,
    }
