
"""
Automated tests for the reusable CICIDS2017
dataset preprocessing pipeline.

Sprint 3 - TEST-02
Jira: KAN-119

Purpose:
    Validate dataset cleaning, schema normalization,
    label normalization, missing-value handling,
    infinite-value handling, duplicate removal,
    invalid inputs, reproducibility, and reusability.

Run:
    python -m pytest tests/test_dataset_preprocessing.py -v
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
    Small controlled CICIDS2017-style dataset.

    Includes:
        - Whitespace in column names
        - Whitespace in traffic labels
        - Multiple traffic classes
        - Numerical network-flow features
    """

    return pd.DataFrame({
        " Flow Duration ": [100, 200, 300],
        "Total Fwd Packets": [10, 20, 30],
        "Flow Bytes/s": [
            1000.0,
            2000.0,
            3000.0,
        ],
        " Label ": [
            " BENIGN ",
            "DoS Hulk ",
            " PortScan",
        ],
    })


# ==================================================
# TEST 1: SCHEMA CONSISTENCY
# ==================================================

def test_schema_consistency(sample_dataset):
    """
    Verify that column names are normalized
    by removing leading and trailing whitespace.
    """

    cleaned, summary = preprocess_dataset(
        sample_dataset
    )

    assert "Flow Duration" in cleaned.columns
    assert "Label" in cleaned.columns

    assert all(
        column == column.strip()
        for column in cleaned.columns
    )

    assert len(cleaned) == 3


# ==================================================
# TEST 2: LABEL NORMALIZATION
# ==================================================

def test_label_normalization(sample_dataset):
    """
    Verify that traffic labels have whitespace
    removed without changing attack class names.
    """

    cleaned, summary = preprocess_dataset(
        sample_dataset
    )

    assert cleaned["Label"].tolist() == [
        "BENIGN",
        "DoS Hulk",
        "PortScan",
    ]


# ==================================================
# TEST 3: MISSING VALUES
# ==================================================

def test_missing_values():
    """
    Verify that records containing missing values
    are removed from the cleaned dataset.
    """

    df = pd.DataFrame({
        "Flow Duration": [
            100,
            np.nan,
            300,
        ],
        "Label": [
            "BENIGN",
            "BENIGN",
            "DoS Hulk",
        ],
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
    """
    Verify that positive and negative infinity
    values are removed.
    """

    df = pd.DataFrame({
        "Flow Bytes/s": [
            100.0,
            np.inf,
            -np.inf,
        ],
        "Label": [
            "BENIGN",
            "DoS Hulk",
            "PortScan",
        ],
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
    """
    Verify that identical records are removed
    while retaining the first occurrence.
    """

    df = pd.DataFrame({
        "Flow Duration": [
            100,
            100,
            200,
        ],
        "Label": [
            "BENIGN",
            "BENIGN",
            "DoS Hulk",
        ],
    })

    cleaned, summary = preprocess_dataset(df)

    assert len(cleaned) == 2

    assert summary["duplicates_found"] == 1

    assert summary["remaining_duplicates"] == 0


# ==================================================
# TEST 6: ORIGINAL DATAFRAME PRESERVATION
# ==================================================

def test_original_dataframe_unchanged(
    sample_dataset,
):
    """
    Ensure preprocessing does not modify
    the original input DataFrame.
    """

    original = sample_dataset.copy(deep=True)

    preprocess_dataset(sample_dataset)

    assert_frame_equal(
        sample_dataset,
        original,
    )


# ==================================================
# TEST 7: INVALID INPUT HANDLING
# ==================================================

def test_invalid_input():
    """
    Verify that non-DataFrame input raises
    a TypeError.
    """

    with pytest.raises(
        TypeError,
        match="pandas DataFrame",
    ):
        preprocess_dataset(
            [100, 200, 300]
        )


# ==================================================
# TEST 8: EMPTY DATASET HANDLING
# ==================================================

def test_empty_dataframe():
    """
    Verify that an empty DataFrame can be
    processed without division-by-zero errors.
    """

    df = pd.DataFrame(
        columns=[
            "Flow Duration",
            "Label",
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
    """
    Verify that records containing missing
    traffic labels are removed.
    """

    df = pd.DataFrame({
        "Flow Duration": [
            100,
            200,
            300,
        ],
        "Label": [
            "BENIGN",
            np.nan,
            "DoS Hulk",
        ],
    })

    cleaned, summary = preprocess_dataset(df)

    assert len(cleaned) == 2

    assert cleaned["Label"].notna().all()

    assert "nan" not in cleaned[
        "Label"
    ].values

    assert summary["rows_with_missing"] == 1


# ==================================================
# TEST 10: NEGATIVE PACKET COUNTS
# ==================================================

def test_negative_packet_counts_retained():
    """
    Current preprocessing policy retains
    finite negative packet counts.

    This is a known data-quality limitation
    and should be reviewed in future work.
    """

    df = pd.DataFrame({
        "Total Fwd Packets": [
            10,
            -5,
            20,
        ],
        "Flow Duration": [
            100,
            200,
            300,
        ],
        "Label": [
            "BENIGN",
            "BENIGN",
            "DoS Hulk",
        ],
    })

    cleaned, summary = preprocess_dataset(df)

    assert -5 in cleaned[
        "Total Fwd Packets"
    ].values


# ==================================================
# TEST 11: NEGATIVE FLOW DURATION
# ==================================================

def test_negative_flow_duration_retained():
    """
    Current preprocessing policy retains
    finite negative flow durations.

    Negative durations are not valid physical
    measurements and require future handling.
    """

    df = pd.DataFrame({
        "Flow Duration": [
            100,
            -200,
            300,
        ],
        "Total Fwd Packets": [
            10,
            20,
            30,
        ],
        "Label": [
            "BENIGN",
            "DoS Hulk",
            "PortScan",
        ],
    })

    cleaned, summary = preprocess_dataset(df)

    assert -200 in cleaned[
        "Flow Duration"
    ].values


# ==================================================
# TEST 12: PREPROCESSING SUMMARY
# ==================================================

def test_summary_row_counts():
    """
    Verify that the pipeline accurately reports
    removed records and removal percentages.
    """

    df = pd.DataFrame({
        "Flow Duration": [
            100,
            100,
            np.nan,
            200,
        ],
        "Label": [
            "BENIGN",
            "BENIGN",
            "DoS Hulk",
            "PortScan",
        ],
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
    """
    Verify that running preprocessing multiple
    times on the same input produces the same
    output and summary statistics.
    """

    cleaned1, summary1 = preprocess_dataset(
        sample_dataset
    )

    cleaned2, summary2 = preprocess_dataset(
        sample_dataset
    )

    assert_frame_equal(
        cleaned1,
        cleaned2,
    )

    assert summary1 == summary2


# ==================================================
# TEST 14: COLUMN ORDER INDEPENDENCE
# ==================================================

def test_column_order_independence(
    sample_dataset,
):
    """
    Verify that the dataset-cleaning behavior
    does not depend on input column order.

    This test compares equivalent outputs
    after sorting columns.
    """

    reordered = sample_dataset[
        list(reversed(sample_dataset.columns))
    ]

    cleaned1, _ = preprocess_dataset(
        sample_dataset
    )

    cleaned2, _ = preprocess_dataset(
        reordered
    )

    assert_frame_equal(
        cleaned1.sort_index(axis=1),
        cleaned2.sort_index(axis=1),
    )


# ==================================================
# TEST 15: COMPLETELY MISSING RECORD
# ==================================================

def test_completely_missing_row_removed():
    """
    Verify that a record containing missing
    feature values and a missing label is removed.
    """

    df = pd.DataFrame({
        "Flow Duration": [
            100,
            np.nan,
            300,
        ],
        "Total Fwd Packets": [
            10,
            np.nan,
            30,
        ],
        "Label": [
            "BENIGN",
            np.nan,
            "DoS Hulk",
        ],
    })

    cleaned, summary = preprocess_dataset(df)

    assert len(cleaned) == 2

    assert cleaned.isna().sum().sum() == 0

    assert summary["rows_removed"] == 1


# ==================================================
# TEST 16: COMBINED DATA QUALITY ISSUES
# ==================================================

def test_combined_preprocessing_issues():
    """
    Verify that multiple data-quality issues
    are handled correctly in one dataset.

    Issues included:
        - Whitespace in column names
        - Whitespace in labels
        - Duplicate records
        - Infinite numerical values
        - Missing numerical values
    """

    df = pd.DataFrame({
        " Flow Duration ": [
            100,
            100,
            200,
            np.nan,
            300,
        ],
        "Flow Bytes/s": [
            1000.0,
            1000.0,
            np.inf,
            4000.0,
            5000.0,
        ],
        " Label ": [
            " BENIGN ",
            " BENIGN ",
            "DoS Hulk",
            "PortScan",
            " DoS Hulk ",
        ],
    })

    cleaned, summary = preprocess_dataset(df)

    assert len(cleaned) == 2

    assert cleaned["Label"].tolist() == [
        "BENIGN",
        "DoS Hulk",
    ]

    assert summary["rows_before"] == 5

    assert summary["rows_after"] == 2

    assert summary["rows_removed"] == 3

    assert summary["remaining_missing_values"] == 0

    assert summary["remaining_infinite_values"] == 0

    assert summary["remaining_duplicates"] == 0
