
import json
from pathlib import Path

import joblib
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

MODEL_DIR = ROOT / "ml" / "models" / "cicids2017_baseline"

MODEL_PATH = MODEL_DIR / "aegis_cicids2017_binary_rf_v1.joblib"

METADATA_PATH = MODEL_DIR / "aegis_cicids2017_binary_rf_v1.metadata.json"

TEST_DATA_PATH = (
    ROOT
    / "ml"
    / "data"
    / "processed"
    / "model_ready"
    / "CICIDS2017_Binary_test.csv"
)


def main():
    metadata = json.loads(
        METADATA_PATH.read_text(encoding="utf-8")
    )

    # Load only your own trusted trained model.
    model = joblib.load(MODEL_PATH)

    df = pd.read_csv(TEST_DATA_PATH)

    feature_names = metadata["feature_names_ordered"]
    threshold = float(metadata["threshold"])

    # Verify the training/inference feature schema.
    if len(feature_names) != model.n_features_in_:
        raise ValueError("Model feature count mismatch")

    if not set(feature_names).issubset(df.columns):
        raise ValueError("Test dataset is missing model features")

    # Inspect dataset labels and select a known benign record.
    if "Binary_Label" in df.columns:
        label_column = "Binary_Label"
        benign_value = 0
    elif "Label" in df.columns:
        label_column = "Label"
        benign_value = (
            "BENIGN"
            if (df["Label"].astype(str).str.upper() == "BENIGN").any()
            else 0
        )
    else:
        raise ValueError(
            f"Cannot identify label column. Available: {list(df.columns)}"
        )

    benign_rows = df[
        df[label_column].astype(str).str.upper()
        == str(benign_value).upper()
    ]

    if benign_rows.empty:
        raise ValueError("No benign sample found")

    sample = benign_rows.iloc[[0]][feature_names]

    # ATTACK = 1; BENIGN = 0.
    attack_index = list(model.classes_).index(1)

    attack_probability = float(
        model.predict_proba(sample)[0][attack_index]
    )

    predicted_attack = attack_probability >= threshold
    predicted_label = "ATTACK" if predicted_attack else "BENIGN"

    print("=" * 55)
    print("AEGIS - INT-05 BENIGN TRAFFIC CLASSIFICATION")
    print("=" * 55)
    print("Model ID:", metadata["model_id"])
    print("Expected Label: BENIGN")
    print("Predicted Label:", predicted_label)
    print("Attack Probability:", round(attack_probability, 6))
    print("Classification Threshold:", threshold)
    print("Features Used:", len(feature_names))
    print(
        "Classification Correct:",
        predicted_label == "BENIGN",
    )
    print(
        "TEST STATUS:",
        "PASS" if predicted_label == "BENIGN" else "FAIL",
    )


if __name__ == "__main__":
    main()
