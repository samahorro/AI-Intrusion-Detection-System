
"""
Automated tests for the reusable CIC-IDS2017
dataset preprocessing pipeline.

Sprint 3 - TEST-02
Jira: KAN-119
"""

import numpy as np
import pandas as pd
import pytest

from pandas.testing import assert_frame_equal

from ml.preprocessing.preprocess import preprocess_dataset


# ==================================================
# REUSABLE TEST DATA
# ==================================================

@pytest.fixture
def sample_dataset():
    """
    Small controlled CIC-IDS2017-style dataset.
    """

    return pd.DataFrame({
        " Flow Duration ": [100, 200, 300],
        "Total Fwd Packets": [10, 20, 30],
        "Flow Bytes/s": [1000.0, 2000.0, 3000.0],
        " Label ": [
            " BENIGN ",
            "DoS Hulk ",
            " PortScan"
        ]
    })


# ==================================================
# TEST 1: SCHEMA CONSISTENCY
# ==================================================

def test_schema_consistency(sample_dataset):

    cleaned, summary = preprocess_dataset(sample_dataset)

    assert "Flow Duration" in cleaned.columns
    assert "Label" in cleaned.columns

    assert all(
        column == column.strip()
        for column in cleaned.columns
    )


# ==================================================
# TEST 2: LABEL NORMALIZATION
# ==================================================

def test_label_normalization(sample_dataset):

    cleaned, summary = preprocess_dataset(sample_dataset)

    assert cleaned["Label"].tolist() == [
        "BENIGN",
        "DoS Hulk",
        "PortScan"
    ]


# ==================================================
# TEST 3: MISSING VALUES
# ==================================================

def test_missing_values():

    df = pd.DataFrame({
        "Flow Duration": [100, np.nan, 300],
        "Label": [
            "BENIGN",
            "BENIGN",
            "DoS Hulk"
        ]
    })

    cleaned, summary = preprocess_dataset(df)

    assert len(cleaned) == 2

    assert cleaned.isna().sum().sum() == 0

    assert summary["rows_with_missing"] == 1

    assert summary["remaining_missing_values"] == 0


# ==================================================
# TEST 4: INFINITE VALUES
# ==================================================

def test_infinite_values():

    df = pd.DataFrame({
        "Flow Bytes/s": [
            100.0,
            np.inf,
            -np.inf
        ],
        "Label": [
            "BENIGN",
            "DoS Hulk",
            "PortScan"
        ]
    })

    cleaned, summary = preprocess_dataset(df)

    assert len(cleaned) == 1

    numeric_values = cleaned.select_dtypes(
        include=[np.number]
    ).to_numpy()

    assert not np.isinf(
        numeric_values
    ).any()

    assert summary["remaining_infinite_values"] == 0


# ==================================================
# TEST 5: DUPLICATE REMOVAL
# ==================================================

def test_duplicate_removal():

    df = pd.DataFrame({
        "Flow Duration": [100, 100, 200],
        "Label": [
            "BENIGN",
            "BENIGN",
            "DoS Hulk"
        ]
    })

    cleaned, summary = preprocess_dataset(df)

    assert len(cleaned) == 2

    assert summary["duplicates_found"] == 1

    assert summary["remaining_duplicates"] == 0


# ==================================================
# TEST 6: ORIGINAL DATAFRAME PRESERVATION
# ==================================================

def test_original_dataframe_unchanged(sample_dataset):

    original = sample_dataset.copy(deep=True)

    preprocess_dataset(sample_dataset)

    assert_frame_equal(
        sample_dataset,
        original
    )


# ==================================================
# TEST 7: INVALID INPUT HANDLING
# ==================================================

def test_invalid_input():

    with pytest.raises(
        TypeError,
        match="pandas DataFrame"
    ):
        preprocess_dataset([100, 200, 300])


# ==================================================
# TEST 8: EMPTY DATASET HANDLING
# ==================================================

def test_empty_dataframe():

    df = pd.DataFrame(
        columns=[
            "Flow Duration",
            "Label"
        ]
    )

    cleaned, summary = preprocess_dataset(df)

    assert cleaned.empty

    assert summary["rows_before"] == 0
    assert summary["rows_after"] == 0
    assert summary["percent_removed"] == 0


# ==================================================
# TEST 9: MISSING TRAFFIC LABELS
# ==================================================

def test_missing_traffic_labels():

    df = pd.DataFrame({
        "Flow Duration": [100, 200, 300],
        "Label": [
            "BENIGN",
            np.nan,
            "DoS Hulk"
        ]
    })

    cleaned, summary = preprocess_dataset(df)

    assert len(cleaned) == 2

    assert cleaned["Label"].notna().all()

    assert "nan" not in cleaned["Label"].values

    assert summary["rows_with_missing"] == 1


# ==================================================
# TEST 10: NEGATIVE PACKET COUNTS
# ==================================================

def test_negative_packet_counts_retained():

    df = pd.DataFrame({
        "Total Fwd Packets": [10, -5, 20],
        "Flow Duration": [100, 200, 300],
        "Label": [
            "BENIGN",
            "BENIGN",
            "DoS Hulk"
        ]
    })

    cleaned, summary = preprocess_dataset(df)

    # Current policy retains finite negative values.
    # These anomalies require further investigation.

    assert -5 in cleaned[
        "Total Fwd Packets"
    ].values


# ==================================================
# TEST 11: NEGATIVE FLOW DURATION
# ==================================================

def test_negative_flow_duration_retained():

    df = pd.DataFrame({
        "Flow Duration": [100, -200, 300],
        "Total Fwd Packets": [10, 20, 30],
        "Label": [
            "BENIGN",
            "DoS Hulk",
            "PortScan"
        ]
    })

    cleaned, summary = preprocess_dataset(df)

    # Current policy retains finite negative durations.

    assert -200 in cleaned[
        "Flow Duration"
    ].values


# ==================================================
# TEST 12: PREPROCESSING SUMMARY
# ==================================================

def test_summary_row_counts():

    df = pd.DataFrame({
        "Flow Duration": [
            100,
            100,
            np.nan,
            200
        ],
        "Label": [
            "BENIGN",
            "BENIGN",
            "DoS Hulk",
            "PortScan"
        ]
    })

    cleaned, summary = preprocess_dataset(df)

    assert summary["rows_before"] == 4
    assert summary["rows_after"] == 2
    assert summary["rows_removed"] == 2
    assert summary["percent_removed"] == 50.0


# ==================================================
# TEST 13: REPEATABILITY
# ==================================================

def test_repeatability(sample_dataset):

    cleaned1, summary1 = preprocess_dataset(
        sample_dataset
    )

    cleaned2, summary2 = preprocess_dataset(
        sample_dataset
    )

    assert_frame_equal(
        cleaned1,
        cleaned2
    )

    assert summary1 == summary2
