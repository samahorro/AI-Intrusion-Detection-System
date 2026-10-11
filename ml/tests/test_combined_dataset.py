
"""
TEST-03 — Validate Combined CICIDS2017 Dataset

Sprint 3
Jira: KAN-121

Validates the combined dataset produced by Notebook 09.

Run from the repository root:
    python -m pytest ml/tests/test_combined_dataset.py -v
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = PROJECT_ROOT / "ml" / "data" / "processed"

COMBINED_PATH = (
    PROCESSED_DIR
    / "combined"
    / "CICIDS2017_Combined_Cleaned.csv"
)

EXPECTED_ROWS = 2_572_527
EXPECTED_COLUMNS = 81
EXPECTED_NUMERIC_FEATURES = 78

SOURCE_FILES = {
    "Monday - BENIGN": "Monday-WorkingHours-Cleaned.csv",
    "Tuesday - Brute Force": "Tuesday-WorkingHours-Cleaned.csv",
    "Wednesday - DoS and Heartbleed": "Wednesday-WorkingHours-Cleaned.csv",
    "Thursday Morning - Web Attacks": "Thursday-Morning-WebAttacks-Cleaned.csv",
    "Thursday Afternoon - Infiltration": "Thursday-Afternoon-Infiltration-Cleaned.csv",
    "Friday Morning - Botnet": "Friday-Morning-Botnet-Cleaned.csv",
    "Friday Afternoon - PortScan": "Friday-Afternoon-PortScan-Cleaned.csv",
    "Friday Afternoon - DDoS": "Friday-Afternoon-DDoS-Cleaned.csv",
}

MODEL_FEATURES = [
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Flow Bytes/s",
    "Flow Packets/s",
]


@pytest.fixture(scope="module")
def combined_dataset():
    """Load the combined dataset only once for this test module."""
    if not COMBINED_PATH.is_file():
        pytest.fail(f"Combined dataset not found: {COMBINED_PATH}")

    return pd.read_csv(COMBINED_PATH, low_memory=False)


# ==================================================
# TEST 1 — DATASET LOADING
# ==================================================

def test_combined_dataset_loads(combined_dataset):
    assert isinstance(combined_dataset, pd.DataFrame)
    assert not combined_dataset.empty


# ==================================================
# TEST 2 — ROW COUNT
# ==================================================

def test_expected_row_count(combined_dataset):
    assert len(combined_dataset) == EXPECTED_ROWS


# ==================================================
# TEST 3 — SCHEMA
# ==================================================

def test_schema_consistency(combined_dataset):
    df = combined_dataset

    assert len(df.columns) == EXPECTED_COLUMNS
    assert df.columns.is_unique

    assert all(col == col.strip() for col in df.columns)

    required = {"SourceDataset", "SourceRow", "Label"}
    assert required.issubset(df.columns)

    feature_columns = [
        col for col in df.columns
        if col not in required
    ]

    assert len(feature_columns) == EXPECTED_NUMERIC_FEATURES


# ==================================================
# TEST 4 — MISSING VALUES
# ==================================================

def test_no_missing_values(combined_dataset):
    assert not combined_dataset.isna().any().any()


# ==================================================
# TEST 5 — INFINITE VALUES
# ==================================================

def test_no_infinite_numeric_values(combined_dataset):
    df = combined_dataset

    feature_columns = [
        col for col in df.columns
        if col not in {"SourceDataset", "SourceRow", "Label"}
    ]

    for column in feature_columns:
        values = df[column].to_numpy(dtype=np.float64)
        assert np.isfinite(values).all(), (
            f"Non-finite values found in {column}"
        )


# ==================================================
# TEST 6 — NEGATIVE FLOW DURATION
# ==================================================

def test_no_negative_flow_duration(combined_dataset):
    assert (
        combined_dataset["Flow Duration"] >= 0
    ).all()


# ==================================================
# TEST 7 — SOURCE TRACKING
# ==================================================

def test_source_tracking_columns(combined_dataset):
    df = combined_dataset

    assert df["SourceDataset"].notna().all()
    assert df["SourceRow"].notna().all()

    assert (df["SourceRow"] >= 0).all()

    assert not df.duplicated(
        subset=["SourceDataset", "SourceRow"]
    ).any()


# ==================================================
# TEST 8 — ALL EIGHT DATASETS PRESENT
# ==================================================

def test_all_source_datasets_present(combined_dataset):
    actual_sources = set(
        combined_dataset["SourceDataset"].unique()
    )

    expected_sources = set(SOURCE_FILES)

    assert actual_sources == expected_sources


# ==================================================
# TEST 9 — TRAFFIC LABELS
# ==================================================

def test_traffic_labels(combined_dataset):
    labels = combined_dataset["Label"]

    assert labels.notna().all()
    assert labels.astype(str).str.strip().ne("").all()

    assert "BENIGN" in labels.values
    assert labels.ne("BENIGN").any()

    assert labels.equals(labels.astype(str).str.strip())


# ==================================================
# TEST 10 — MODEL FEATURE COMPATIBILITY
# ==================================================

def test_model_features(combined_dataset):
    df = combined_dataset

    for feature in MODEL_FEATURES:
        assert feature in df.columns
        assert pd.api.types.is_numeric_dtype(df[feature])


# ==================================================
# TEST 11 — SOURCE ROW RECONCILIATION
# ==================================================

def test_source_row_counts(combined_dataset):
    actual_counts = (
        combined_dataset["SourceDataset"]
        .value_counts()
        .to_dict()
    )

    expected_counts = {}

    for source_name, filename in SOURCE_FILES.items():
        source_path = PROCESSED_DIR / filename

        assert source_path.is_file(), (
            f"Missing cleaned source: {source_path}"
        )

        with source_path.open(
            "r", encoding="utf-8-sig", newline=""
        ) as file:
            # CICIDS2017 cleaned records do not normally contain
            # embedded newlines. Count CSV records reliably using
            # pandas chunks instead of physical text lines.
            count = 0
            for chunk in pd.read_csv(
                file,
                usecols=[0],
                chunksize=100_000,
            ):
                count += len(chunk)

        expected_counts[source_name] = count

    assert actual_counts == expected_counts
