import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ml.preprocessing.preprocess import preprocess_dataset


def manual_validate(csv_path):
    print("=" * 60)
    print("TEST-02: MANUAL DATASET PREPROCESSING VALIDATION")
    print("=" * 60)

    # Load representative CIC-IDS2017 dataset
    df = pd.read_csv(csv_path, low_memory=False)

    print("\nMT-01: ORIGINAL DATASET STRUCTURE")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))
    print("Sample columns:", df.columns.tolist()[:10])

    # Run reusable preprocessing pipeline
    cleaned, summary = preprocess_dataset(df)

    print("\nMT-02: MISSING AND INFINITE VALUES")
    numeric = cleaned.select_dtypes(include=[np.number])

    print("Remaining missing values:", cleaned.isna().sum().sum())
    print(
        "Remaining infinite values:",
        np.isinf(numeric.to_numpy()).sum()
    )

    print("\nMT-03: DUPLICATE REMOVAL")
    print("Remaining duplicate rows:", cleaned.duplicated().sum())

    print("\nMT-04: TRAFFIC LABEL VALIDATION")
    if "Label" in cleaned.columns:
        print(cleaned["Label"].value_counts().head(15))
        print(
            "Labels with surrounding whitespace:",
            cleaned["Label"].ne(
                cleaned["Label"].str.strip()
            ).sum()
        )
    else:
        print("WARNING: Label column not found.")

    print("\nMT-05: ANOMALOUS FEATURE INSPECTION")

    columns_to_check = [
        "Flow Duration",
        "Total Fwd Packets",
        "Total Backward Packets",
        "Fwd Header Length",
        "Fwd Header Length.1",
    ]

    for column in columns_to_check:
        if column in cleaned.columns:
            values = pd.to_numeric(
                cleaned[column], errors="coerce"
            )
            print(
                f"{column}: "
                f"min={values.min()}, "
                f"max={values.max()}, "
                f"negative_count={(values < 0).sum()}"
            )

    print("\nMT-06: PREPROCESSING SUMMARY")
    for key, value in summary.items():
        print(f"{key}: {value}")

    print("\nMANUAL VALIDATION COMPLETE")
    print("Review anomalous values before model training.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "csv_path",
        type=Path,
        help="Path to a local CIC-IDS2017 CSV file",
    )
    args = parser.parse_args()

    manual_validate(args.csv_path)
