
"""
Reusable validation functions for combined CICIDS2017 datasets.

Jira: KAN-121
"""

import numpy as np
import pandas as pd


MODEL_FEATURES = [
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Flow Bytes/s",
    "Flow Packets/s",
]


def validate_combined_dataset(
    df: pd.DataFrame,
    expected_rows: int | None = None,
    expected_sources: set[str] | None = None,
) -> dict:
    """
    Validate the structure and quality of a combined
    CICIDS2017 dataset.

    Returns a summary dictionary.

    Raises ValueError when a validation rule fails.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Expected a pandas DataFrame")

    if df.empty:
        raise ValueError("Dataset is empty")

    if not df.columns.is_unique:
        raise ValueError("Duplicate column names found")

    if any(col != col.strip() for col in df.columns):
        raise ValueError("Column names contain whitespace")

    required = {
        "SourceDataset",
        "SourceRow",
        "Label",
        *MODEL_FEATURES,
    }

    missing_columns = required - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    if expected_rows is not None and len(df) != expected_rows:
        raise ValueError(
            f"Expected {expected_rows} rows, found {len(df)}"
        )

    if df.isna().any().any():
        raise ValueError("Missing values found")

    feature_columns = [
        col for col in df.columns
        if col not in {"SourceDataset", "SourceRow", "Label"}
    ]

    for column in feature_columns:
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValueError(
                f"Non-numeric feature: {column}"
            )

        values = df[column].to_numpy(dtype=np.float64)

        if not np.isfinite(values).all():
            raise ValueError(
                f"Infinite or non-finite values: {column}"
            )

    if (df["Flow Duration"] < 0).any():
        raise ValueError("Negative flow duration found")

    if not pd.api.types.is_numeric_dtype(df["SourceRow"]):
        raise ValueError("SourceRow must be numeric")

    source_rows = df["SourceRow"].to_numpy(dtype=np.float64)
    if not np.isfinite(source_rows).all():
        raise ValueError("Invalid SourceRow values found")

    if (source_rows < 0).any():
        raise ValueError("Negative SourceRow found")

    if (source_rows != np.floor(source_rows)).any():
        raise ValueError("SourceRow must contain integers")

    if df.duplicated(
        subset=["SourceDataset", "SourceRow"]
    ).any():
        raise ValueError("Duplicate source identifiers found")

    labels = df["Label"].astype(str)

    if labels.str.strip().eq("").any():
        raise ValueError("Blank traffic labels found")

    if not labels.equals(labels.str.strip()):
        raise ValueError("Traffic labels contain whitespace")

    if "BENIGN" not in labels.values:
        raise ValueError("BENIGN class not found")

    if not labels.ne("BENIGN").any():
        raise ValueError("Attack class not found")

    actual_sources = set(df["SourceDataset"].unique())

    if expected_sources is not None:
        if actual_sources != expected_sources:
            raise ValueError(
                "Source datasets do not match expected sources"
            )

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "sources": len(actual_sources),
        "classes": int(df["Label"].nunique()),
        "missing_values": 0,
        "infinite_values": 0,
        "status": "passed",
    }
