
"""
AEGIS - INT-06 Suspicious Traffic Classification

Tests the trained CIC-IDS2017 Random Forest model
against a known malicious sample from the held-out
test dataset.

Expected label: ATTACK
"""

import json
from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd


# ==================================================
# FILE PATHS
# ==================================================

ROOT = Path(__file__).resolve().parents[2]

MODEL_DIR = (
    ROOT / "ml" / "models" / "cicids2017_baseline"
)

MODEL_PATH = (
    MODEL_DIR / "aegis_cicids2017_binary_rf_v1.joblib"
)

METADATA_PATH = (
    MODEL_DIR
    / "aegis_cicids2017_binary_rf_v1.metadata.json"
)

TEST_DATA_PATH = (
    ROOT
    / "ml"
    / "data"
    / "processed"
    / "model_ready"
    / "CICIDS2017_Binary_test.csv"
)


# ==================================================
# IDENTIFY LABELED ATTACK SAMPLES
# ==================================================

def get_attack_mask(df):
    """Identify known malicious records safely."""

    # Prefer an explicit binary label when available.
    if "Binary_Label" in df.columns:
        label_column = "Binary_Label"
    elif "Label" in df.columns:
        label_column = "Label"
    else:
        raise ValueError(
            "No supported label column found. "
            f"Available columns: {list(df.columns)}"
        )

    labels = df[label_column]

    print("Label Column:", label_column)
    print("\nDataset Label Distribution:")
    print(labels.value_counts(dropna=False).head(20))
    print()

    # Support numeric binary labels:
    # 0 = BENIGN, 1 = ATTACK
    numeric_labels = pd.to_numeric(
        labels,
        errors="coerce",
    )

    if numeric_labels.notna().all():
        unknown_values = set(
            numeric_labels.unique()
        ) - {0, 1}

        if unknown_values:
            raise ValueError(
                "Unexpected numeric labels: "
                f"{sorted(unknown_values)}"
            )

        return numeric_labels.eq(1)

    # Support textual labels.
    normalized = (
        labels.astype(str)
        .str.strip()
        .str.upper()
    )

    benign_values = {
        "0",
        "0.0",
        "BENIGN",
        "NORMAL",
    }

    attack_values = {
        "1",
        "1.0",
        "ATTACK",
        "MALICIOUS",
        "PORTSCAN",
        "PORT SCAN",
        "DDOS",
        "DOS HULK",
        "DOS GOLDENEYE",
        "DOS SLOWLORIS",
        "DOS SLOWHTTPTEST",
        "FTP-PATATOR",
        "SSH-PATATOR",
        "BOT",
        "INFILTRATION",
        "HEARTBLEED",
        "WEB ATTACK - BRUTE FORCE",
        "WEB ATTACK - XSS",
        "WEB ATTACK - SQL INJECTION",
    }

    recognized_values = benign_values | attack_values

    unknown_labels = (
        set(normalized.unique()) - recognized_values
    )

    if unknown_labels:
        raise ValueError(
            "Unrecognized dataset labels: "
            f"{sorted(unknown_labels)}"
        )

    return normalized.isin(attack_values)


# ==================================================
# RUN INT-06 TEST
# ==================================================

def main():

    print("=" * 60)
    print(
        "AEGIS - INT-06 SUSPICIOUS TRAFFIC CLASSIFICATION"
    )
    print("=" * 60)

    timestamp = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )

    print("Test Timestamp:", timestamp)

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
    # LOAD MODEL METADATA
    # ----------------------------------------------

    metadata = json.loads(
        METADATA_PATH.read_text(
            encoding="utf-8"
        )
    )

    feature_names = metadata["feature_names_ordered"]
    threshold = float(metadata["threshold"])

    if not 0 <= threshold <= 1:
        raise ValueError(
            "Classification threshold must be between 0 and 1"
        )

    # ----------------------------------------------
    # LOAD TRAINED RANDOM FOREST
    # ----------------------------------------------

    # Only load model artifacts you created or trust.
    model = joblib.load(MODEL_PATH)

    if not hasattr(model, "predict_proba"):
        raise ValueError(
            "Model does not support probability predictions"
        )

    if len(feature_names) != model.n_features_in_:
        raise ValueError(
            "Model feature count does not match metadata"
        )

    if 1 not in model.classes_:
        raise ValueError(
            "Model does not contain ATTACK class 1"
        )

    # ----------------------------------------------
    # LOAD HELD-OUT TEST DATASET
    # ----------------------------------------------

    df = pd.read_csv(TEST_DATA_PATH)

    missing_features = [
        feature
        for feature in feature_names
        if feature not in df.columns
    ]

    if missing_features:
        raise ValueError(
            "Dataset is missing required features: "
            f"{missing_features}"
        )

    # ----------------------------------------------
    # SELECT A KNOWN ATTACK SAMPLE
    # ----------------------------------------------

    attack_mask = get_attack_mask(df)

    attack_rows = df.loc[attack_mask]

    print(
        "Attack Samples Available:",
        len(attack_rows),
    )

    if attack_rows.empty:
        raise ValueError(
            "No labeled attack samples found"
        )

    # Select the first ATTACK sample deterministically.
    # Do not choose a sample based on model prediction.
    sample = attack_rows.iloc[[0]][feature_names]

    sample_index = attack_rows.index[0]

    # ----------------------------------------------
    # VERIFY SAMPLE FEATURES
    # ----------------------------------------------

    sample = sample.apply(
        pd.to_numeric,
        errors="coerce",
    )

    if sample.isna().any().any():
        raise ValueError(
            "Selected sample contains missing or invalid features"
        )

    # ----------------------------------------------
    # RUN AI CLASSIFICATION
    # ----------------------------------------------

    attack_index = list(
        model.classes_
    ).index(1)

    probabilities = model.predict_proba(
        sample
    )

    attack_probability = float(
        probabilities[0][attack_index]
    )

    predicted_attack = (
        attack_probability >= threshold
    )

    predicted_label = (
        "ATTACK"
        if predicted_attack
        else "BENIGN"
    )

    expected_label = "ATTACK"

    classification_correct = (
        predicted_label == expected_label
    )

    # ----------------------------------------------
    # DISPLAY RESULTS
    # ----------------------------------------------

    print()
    print("=" * 60)
    print("AI CLASSIFICATION RESULTS")
    print("=" * 60)

    print("Model ID:", metadata["model_id"])
    print(
        "Sample Source:",
        TEST_DATA_PATH.name,
    )
    print("Sample Row Index:", sample_index)
    print("Expected Label:", expected_label)
    print("Predicted Label:", predicted_label)

    print(
        "Attack Probability:",
        round(attack_probability, 6),
    )

    print(
        "Classification Threshold:",
        threshold,
    )

    print(
        "Features Used:",
        len(feature_names),
    )

    print(
        "Classification Correct:",
        classification_correct,
    )

    print()
    print("=" * 60)

    print(
        "TEST STATUS:",
        "PASS" if classification_correct else "FAIL",
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
