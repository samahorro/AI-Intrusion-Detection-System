
import json
from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd


# -----------------------------------------------
# FILE PATHS
# -----------------------------------------------

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


def main():

    # -----------------------------------------------
    # LOAD TRAINED MODEL AND METADATA
    # -----------------------------------------------

    metadata = json.loads(
        METADATA_PATH.read_text(encoding="utf-8")
    )

    # Load only trusted, locally trained artifacts.
    model = joblib.load(MODEL_PATH)

    feature_names = metadata["feature_names_ordered"]
    threshold = float(metadata["threshold"])

    # -----------------------------------------------
    # LOAD LABELED TEST DATASET
    # -----------------------------------------------

    df = pd.read_csv(TEST_DATA_PATH)

    if len(feature_names) != model.n_features_in_:
        raise ValueError("Model feature count mismatch")

    if not set(feature_names).issubset(df.columns):
        raise ValueError("Test dataset is missing model features")

    # -----------------------------------------------
    # IDENTIFY KNOWN ATTACK RECORDS
    # -----------------------------------------------

    if "Binary_Label" in df.columns:
        label_column = "Binary_Label"

    elif "Label" in df.columns:
        label_column = "Label"

    else:
        raise ValueError(
            "No supported label column found. "
            f"Available columns: {list(df.columns)}"
        )

    normalized_labels = (
        df[label_column]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    attack_rows = df[
        normalized_labels.isin(["1", "ATTACK", "MALICIOUS"])
    ]

    if attack_rows.empty:
        raise ValueError("No labeled attack samples found")

    # Deterministic first attack row from held-out data.
    sample = attack_rows.iloc[[0]][feature_names]

    # -----------------------------------------------
    # RUN RANDOM FOREST PREDICTION
    # -----------------------------------------------

    attack_index = list(model.classes_).index(1)

    attack_probability = float(
        model.predict_proba(sample)[0][attack_index]
    )

    predicted_attack = attack_probability >= threshold

    predicted_label = (
        "ATTACK" if predicted_attack else "BENIGN"
    )

    classification_correct = predicted_label == "ATTACK"

    # -----------------------------------------------
    # DISPLAY TEST RESULTS
    # -----------------------------------------------

    print("=" * 58)
    print("AEGIS - INT-06 SUSPICIOUS TRAFFIC CLASSIFICATION")
    print("=" * 58)

    print("Test Timestamp:", datetime.now().astimezone().isoformat(timespec="seconds"))
    print("Model ID:", metadata["model_id"])
    print("Sample Source: CICIDS2017_Binary_test.csv")
    print("Expected Label: ATTACK")
    print("Predicted Label:", predicted_label)
    print("Attack Probability:", round(attack_probability, 6))
    print("Classification Threshold:", threshold)
    print("Features Used:", len(feature_names))
    print("Classification Correct:", classification_correct)

    print(
        "TEST STATUS:",
        "PASS" if classification_correct else "FAIL"
    )


if __name__ == "__main__":
    main()
