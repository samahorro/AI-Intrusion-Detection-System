
"""Authenticated capture and experimental intrusion-detection API."""

import json
import math
import os
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ml.models.inference import load_model
from ml.preprocessing.flow_preprocessor import REQUIRED_FEATURES

from ..auth.dependencies import require_authenticated_user
from .capture_service import capture_service
from .interface_service import list_capture_interfaces


# ==================================================
# CAPTURE ROUTER
# All capture and experimental AI endpoints require
# an authenticated user session.
# ==================================================

router = APIRouter(
    prefix="/capture",
    tags=["capture"],
    dependencies=[
        Depends(require_authenticated_user),
    ],
)


class StartCaptureRequest(BaseModel):
    interface: str


# ==================================================
# GET AVAILABLE NETWORK INTERFACES
# ==================================================

@router.get("/interfaces")
def get_interfaces():
    try:
        return {
            "interfaces": list_capture_interfaces()
        }
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc


# ==================================================
# GET LIVE CAPTURE STATUS
# ==================================================

@router.get("/status")
def get_status():
    running = capture_service.is_running()

    return {
        "running": running,
        "interface": (
            capture_service.interface
            if running
            else None
        ),
    }


# ==================================================
# GET LIVE CAPTURE STATISTICS
# ==================================================

@router.get("/stats")
def get_stats():
    return capture_service.get_stats()


# ==================================================
# GET NETWORK FLOW PREVIEW
# ==================================================

@router.get("/flows")
def get_flow_preview():
    return capture_service.flow_bridge.snapshot()


# ==================================================
# GET SIGNATURE-BASED SECURITY ALERTS
# KAN-253: Automated Intrusion Detection
# ==================================================

@router.get("/alerts")
def get_security_alerts():
    """Return recent signature-based security alerts.

    Authentication is enforced by the capture router.
    Alerts are generated automatically by FlowBridge
    when captured TCP SYN traffic reaches the
    port-scan detection threshold.

    Alerts are currently stored in memory.
    Experimental ML predictions do not create alerts.
    """

    alerts = capture_service.flow_bridge.get_alerts()

    return {
        "status": "ok",
        "capture_running": capture_service.is_running(),
        "alert_count": len(alerts),
        "alerts": alerts,
    }


# ==================================================
# START LIVE TSHARK CAPTURE
# ==================================================

@router.post("/start")
def start_capture(request: StartCaptureRequest):
    try:
        return capture_service.start(request.interface)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc


# ==================================================
# STOP LIVE TSHARK CAPTURE
# ==================================================

@router.post("/stop")
def stop_capture():
    try:
        return capture_service.stop()

    except RuntimeError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc


# ==================================================
# LOAD EXPERIMENTAL RANDOM FOREST MODEL
# ==================================================

@lru_cache(maxsize=2)
def get_experimental_model(model_path: str):
    """
    Load and cache the trusted trained Random Forest
    model and its metadata.
    """

    path = Path(model_path)

    metadata_path = path.with_suffix(
        ".metadata.json"
    )

    if not metadata_path.is_file():
        raise FileNotFoundError(
            f"Model metadata not found: {metadata_path}"
        )

    metadata = json.loads(
        metadata_path.read_text(
            encoding="utf-8"
        )
    )

    # Ensure model features match preprocessing.
    if (
        metadata.get("feature_names_ordered")
        != REQUIRED_FEATURES
    ):
        raise ValueError(
            "Model feature order does not match preprocessing"
        )

    model = load_model(str(path))

    # Validate model feature count.
    if (
        getattr(model, "n_features_in_", None)
        != len(REQUIRED_FEATURES)
    ):
        raise ValueError(
            "Model expects a different feature count"
        )

    # Confirm that ATTACK class 1 exists.
    if 1 not in model.classes_:
        raise ValueError(
            "Model does not contain ATTACK class 1"
        )

    # Validate saved classification threshold.
    try:
        threshold = float(metadata["threshold"])
    except (TypeError, ValueError, KeyError) as exc:
        raise ValueError(
            "Invalid model threshold"
        ) from exc

    if (
        not math.isfinite(threshold)
        or not 0 <= threshold <= 1
    ):
        raise ValueError(
            "Invalid model threshold"
        )

    return model, metadata


# ==================================================
# EXPERIMENTAL AI INTRUSION DETECTION
#
# TShark -> Packet Capture -> FlowBridge
# -> Feature Vector -> Random Forest
#
# Predictions are experimental only.
# They do not generate security alerts.
# ==================================================

@router.get("/experimental-predictions")
def get_experimental_predictions():
    """
    Classify recently completed network flows
    using the trained Random Forest model.

    Results remain provisional because live
    feature equivalence has not been verified.

    Authentication is enforced by the router.
    """

    model_path = os.getenv("MODEL_PATH")

    if not model_path:
        raise HTTPException(
            status_code=503,
            detail="MODEL_PATH is not configured",
        )

    # Load model and validate metadata.
    try:
        model, metadata = get_experimental_model(
            model_path
        )

    except (
        FileNotFoundError,
        ValueError,
        OSError,
        KeyError,
    ) as exc:
        raise HTTPException(
            status_code=503,
            detail="Experimental model unavailable",
        ) from exc

    # Obtain completed flows from FlowBridge.
    snapshot = (
        capture_service.flow_bridge.snapshot()
    )

    flows = snapshot[
        "experimental_tracking"
    ]["completed_flows"]

    valid_flows = []
    vectors = []

    # ==================================================
    # VALIDATE NETWORK FLOW FEATURE VECTORS
    # ==================================================

    for flow in flows:
        vector = flow["feature_vector"]

        if (
            len(vector) != len(REQUIRED_FEATURES)
            or not all(
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and math.isfinite(value)
                and value >= 0
                for value in vector
            )
        ):
            continue

        valid_flows.append(flow)
        vectors.append(vector)

    predictions = []

    # ==================================================
    # RUN RANDOM FOREST CLASSIFICATION
    # ==================================================

    if vectors:
        attack_index = list(
            model.classes_
        ).index(1)

        probabilities = model.predict_proba(
            vectors
        )

        threshold = float(
            metadata["threshold"]
        )

        for flow, probabilities_row in zip(
            valid_flows,
            probabilities,
        ):
            attack_probability = float(
                probabilities_row[attack_index]
            )

            predicted_attack = (
                attack_probability >= threshold
            )

            predictions.append(
                {
                    "source_ip": flow[
                        "source_ip"
                    ],
                    "destination_ip": flow[
                        "destination_ip"
                    ],
                    "source_port": flow[
                        "source_port"
                    ],
                    "destination_port": flow[
                        "destination_port"
                    ],
                    "protocol": flow[
                        "protocol"
                    ],
                    "packet_count": flow[
                        "packet_count"
                    ],
                    "completion_reason": flow[
                        "completion_reason"
                    ],
                    "features": flow[
                        "features"
                    ],
                    "ai_detection": {
                        "prediction": (
                            "ATTACK"
                            if predicted_attack
                            else "BENIGN"
                        ),
                        "prediction_value": int(
                            predicted_attack
                        ),
                        "attack_probability": (
                            attack_probability
                        ),
                        "threshold": threshold,
                        "model_id": metadata[
                            "model_id"
                        ],
                    },
                }
            )

    # ==================================================
    # EXPERIMENTAL AI RESPONSE
    # ==================================================

    return {
        "status": "experimental",
        "capture_running": (
            capture_service.is_running()
        ),
        "live_feature_equivalence_verified": False,
        "alerts_enabled": False,
        "active_flow_count": snapshot[
            "experimental_tracking"
        ]["active_flow_count"],
        "prediction_count": len(
            predictions
        ),
        "predictions": predictions,
    }
