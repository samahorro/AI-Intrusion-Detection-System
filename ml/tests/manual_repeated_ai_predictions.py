
"""
AEGIS - REG-03 Repeated AI Prediction Requests

Submit multiple valid CIC-IDS2017 test samples to the
trained Random Forest model and verify that prediction
requests complete without errors.

This test validates offline model inference stability.
"""

import json
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# ==================================================
# FILE PATHS
# ==================================================

ROOT = Path(__file__).resolve().parents[2]

MODEL_DIR = ROOT / "ml" / "models" / "cicids2017_baseline"

MODEL_PATH = (
    MODEL_DIR / "aegis_cicids2017_binary_rf_v1.joblib"
)

METADATA_PATH = (
    MODEL_DIR / "aegis_cicids2017_binary_rf_v1.metadata.json"
)

TEST_DATA_PATH = (
    ROOT
    / "ml"
    / "data"
    / "processed"
    / "model_ready"
    / "CICIDS2017_Binary_test.csv"
)

REQUEST_COUNT = 20


def main():
    print("=" * 60)
    print("AEGIS - REG-03 REPEATED AI PREDICTION REQUESTS")
    print("=" * 60)

    print(
        "Test Timestamp:",
        datetime.now().astimezone().isoformat(
            timespec="seconds"
        ),
    )

    # ----------------------------------------------
    # VERIFY REQUIRED FILES
    # ----------------------------------------------

    for path in [
        MODEL_PATH,
        METADATA_PATH,
        TEST_DATA_PATH,
    ]:
        if not path.is_file():
            raise FileNotFoundError(
                f"Required file not found: {path}"
            )

    # ----------------------------------------------
    # LOAD MODEL AND METADATA
    # ----------------------------------------------

    metadata = json.loads(
        METADATA_PATH.read_text(encoding="utf-8")
    )

    model = joblib.load(MODEL_PATH)

    feature_names = metadata["feature_names_ordered"]
    threshold = float(metadata["threshold"])

    if not 0 <= threshold <= 1:
        raise ValueError("Invalid classification threshold")

    if len(feature_names) != model.n_features_in_:
        raise ValueError("Model feature count mismatch")

    if 1 not in model.classes_:
        raise ValueError("ATTACK class is missing from model")

    # ----------------------------------------------
    # LOAD TEST SAMPLES
    # ----------------------------------------------

    df = pd.read_csv(TEST_DATA_PATH)

    missing_features = [
        feature
        for feature in feature_names
        if feature not in df.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing model features: {missing_features}"
        )

    if len(df) < REQUEST_COUNT:
        raise ValueError(
            "Not enough samples for repeated prediction test"
        )

    samples = (
        df[feature_names]
        .sample(n=REQUEST_COUNT, random_state=42)
        .apply(pd.to_numeric, errors="coerce")
    )

    if not np.isfinite(samples.to_numpy()).all():
        raise ValueError(
            "Selected samples contain invalid values"
        )

    # ----------------------------------------------
    # RUN REPEATED PREDICTIONS
    # ----------------------------------------------

    attack_index = list(model.classes_).index(1)

    successful_requests = 0
    failed_requests = 0

    print("Model ID:", metadata["model_id"])
    print("Total Prediction Requests:", REQUEST_COUNT)
    print()

    for request_number, (row_index, row) in enumerate(
        samples.iterrows(),
        start=1,
    ):
        try:
            # Preserve feature names and order.
            sample = pd.DataFrame(
                [row.to_dict()],
                columns=feature_names,
            )

            probability = float(
                model.predict_proba(sample)[0][attack_index]
            )

            if not np.isfinite(probability):
                raise ValueError("Non-finite probability returned")

            predicted_label = (
                "ATTACK"
                if probability >= threshold
                else "BENIGN"
            )

            successful_requests += 1

            print(
                f"Request {request_number:02d}: "
                f"PASS | Row {row_index} | "
                f"Prediction: {predicted_label} | "
                f"Attack Probability: {probability:.6f}"
            )

        except Exception as exc:
            failed_requests += 1

            print(
                f"Request {request_number:02d}: "
                f"FAIL | Error: {exc}"
            )

    # ----------------------------------------------
    # DISPLAY FINAL REGRESSION RESULTS
    # ----------------------------------------------

    overall_pass = (
        successful_requests == REQUEST_COUNT
        and failed_requests == 0
    )

    print()
    print("=" * 60)
    print("REGRESSION TEST SUMMARY")
    print("=" * 60)

    print("Total Requests:", REQUEST_COUNT)
    print("Successful Requests:", successful_requests)
    print("Failed Requests:", failed_requests)
    print("Unexpected Errors:", failed_requests)
    print(
        "TEST STATUS:",
        "PASS" if overall_pass else "FAIL",
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
