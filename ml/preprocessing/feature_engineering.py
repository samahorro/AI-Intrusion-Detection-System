"""Reusable CICIDS2017 feature preparation and deterministic split rules.

Mirrors Notebook 10 cells 5, 9, 11, 13 and 15. No data-dependent
transform is fitted; the original dataframe is not modified.
"""

import numpy as np
import pandas as pd

FEATURES = [
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Flow Bytes/s",
    "Flow Packets/s",
]
METADATA = ["SourceDataset", "SourceRow", "Label"]
TARGET = "BinaryLabel"
SEED = np.uint64(20261010)


def prepare_model_records(data: pd.DataFrame) -> pd.DataFrame:
    """Select five features; filter nonfinite/negative rows; add labels/splits.

    Retains existing source identifiers, and preserves duplicate feature rows.
    FeatureSignature is a 64-bit screening hash, not a proof of unique identity.
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Expected pandas DataFrame")
    required = FEATURES + METADATA
    missing = set(required) - set(data.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    df = data[required].copy()
    if df[METADATA].isna().any().any():
        raise ValueError("Missing source/label metadata")
    if not all(pd.api.types.is_numeric_dtype(df[c]) for c in FEATURES):
        raise ValueError("Model features must be numeric")
    df["Label"] = df["Label"].astype("string").str.strip()
    if df["Label"].eq("").any():
        raise ValueError("Blank traffic label")
    finite = np.isfinite(df[FEATURES].to_numpy(dtype="float64")).all(axis=1)
    nonnegative = (df[FEATURES] >= 0).all(axis=1).to_numpy()
    df = df.loc[finite & nonnegative].copy().reset_index(drop=True)
    if df.empty:
        raise ValueError("No valid model records")
    df[TARGET] = (df["Label"] != "BENIGN").astype("int8")
    signature = pd.util.hash_pandas_object(df[FEATURES], index=False).to_numpy(dtype="uint64")
    df["FeatureSignature"] = signature
    df["Split"] = assign_splits(signature)
    return df


def assign_splits(signatures: np.ndarray) -> np.ndarray:
    """Notebook 10's exact 64-bit mixing and 70/15/15 bucket rules."""
    signatures = np.asarray(signatures, dtype="uint64")
    keys = signatures ^ SEED
    keys = keys ^ (keys >> np.uint64(30))
    keys = keys * np.uint64(0xbf58476d1ce4e5b9)
    keys = keys ^ (keys >> np.uint64(27))
    keys = keys * np.uint64(0x94d049bb133111eb)
    keys = keys ^ (keys >> np.uint64(31))
    bucket = keys % np.uint64(100)
    return np.select([bucket < 70, bucket < 85], ["train", "validation"], default="test")


def split_xy(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Return model-only X and binary y, following Notebook 11."""
    missing = set(FEATURES + [TARGET]) - set(df.columns)
    if missing:
        raise ValueError(f"Missing model columns: {sorted(missing)}")
    x = df[FEATURES].astype("float32")
    y = df[TARGET].astype("int8")
    if not np.isfinite(x.to_numpy()).all():
        raise ValueError("Nonfinite model features")
    if not set(y.unique()).issubset({0, 1}):
        raise ValueError("Target is not binary")
    return x, y
