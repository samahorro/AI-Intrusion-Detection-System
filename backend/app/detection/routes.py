import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ml.detection.signature_detection import detect_signature
from ml.models.inference import load_model, run_inference
from ml.preprocessing.flow_preprocessor import preprocess_flow
from ml.scoring.threat_scoring import score_threat

router = APIRouter(
    prefix="/detection",
    tags=["detection"],
)


class DetectionRequest(BaseModel):
    flow: dict[str, Any]
    event: dict[str, Any] = Field(default_factory=dict)


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


def prediction_is_attack(prediction: Any) -> bool:
    """Normalize model predictions into attack or normal."""

    if isinstance(prediction, str):
        normalized = prediction.strip().lower()

        return normalized not in {
            "0",
            "false",
            "normal",
            "benign",
        }

    return bool(prediction)


def severity_confidence(severity: str) -> float:
    """Convert signature severity to scoring confidence."""

    confidence_map = {
        "normal": 0.0,
        "low": 0.3,
        "medium": 0.6,
        "high": 0.9,
    }

    return confidence_map.get(severity, 0.0)


@router.post("/analyze")
def analyze_network_flow(
    data: DetectionRequest,
    model: Any = Depends(get_detection_model),
):
    """
    Run preprocessing, ML inference, signature detection,
    and threat scoring.
    """

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

    model_detected = prediction_is_attack(
        inference_result["prediction"]
    )

    signature_detected = signature_result["detected"]

    detected = model_detected or signature_detected

    if signature_detected:
        attack_type = signature_result["attack_type"]

        confidence = severity_confidence(
            signature_result["severity"]
        )

    elif model_detected:
        attack_type = "ml_detected"
        confidence = 1.0

    else:
        attack_type = None
        confidence = 0.0

    threat_result = score_threat(
        detected=detected,
        confidence=confidence,
        attack_type=attack_type,
    )

    return {
        "status": "success",
        "features": features,
        "inference": inference_result,
        "signature": signature_result,
        "threat": threat_result,
    }