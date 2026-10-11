
"""
CI-compatible tests for combined CICIDS2017 dataset validation.

Sprint 3 - TEST-03
Jira: KAN-121

These tests use synthetic data and do not require
the full CICIDS2017 dataset.

Run from the repository root:
    python -m pytest ml/tests/test_combined_dataset_ci.py -v
"""

import numpy as np
import pandas as pd
import pytest

from ml.preprocessing.combined_dataset_validator import (
    validate_combined_dataset,
)


# ==================================================
# REUSABLE SYNTHETIC TEST DATA
# ==================================================

@pytest.fixture
def valid_combined_dataset():
    """
    Create a small CICIDS2017-style combined dataset.

    Includes:
        - Five Random Forest features
        - Source dataset identifiers
        - Source row identifiers
        - BENIGN and ATTACK traffic labels
    """

    return pd.DataFrame({
        "Flow Duration": [100, 200, 300, 400],
        "Total Fwd Packets": [10, 20, 30, 40],
        "Total Backward Packets": [5, 10, 15, 20],
        "Flow Bytes/s": [
            1000.0,
            2000.0,
            3000.0,
            4000.0,
        ],
        "Flow Packets/s": [
            150.0,
            200.0,
            250.0,
            300.0,
        ],
        "SourceDataset": [
            "Monday - BENIGN",
            "Monday - BENIGN",
            "Wednesday - DoS and Heartbleed",
            "Wednesday - DoS and Heartbleed",
        ],
        "SourceRow": [0, 1, 0, 1],
        "Label": [
            "BENIGN",
            "BENIGN",
            "DoS Hulk",
            "DoS Hulk",
        ],
    })


# ==================================================
# TEST 1: VALID COMBINED DATASET
# ==================================================

def test_valid_combined_dataset(valid_combined_dataset):
    """
    Verify that a properly structured dataset
    passes all validation checks.
    """

    result = validate_combined_dataset(
        valid_combined_dataset,
        expected_rows=4,
        expected_sources={
            "Monday - BENIGN",
            "Wednesday - DoS and Heartbleed",
        },
    )

    assert result["status"] == "passed"
    assert result["rows"] == 4
    assert result["missing_values"] == 0
    assert result["infinite_values"] == 0


# ==================================================
# TEST 2: MISSING REQUIRED FEATURE
# ==================================================

def test_missing_required_column(valid_combined_dataset):
    """
    Verify that the validator rejects datasets
    missing required model features.
    """

    df = valid_combined_dataset.drop(
        columns=["Flow Duration"]
    )

    with pytest.raises(
        ValueError,
        match="Missing required"
    ):
        validate_combined_dataset(df)


# ==================================================
# TEST 3: MISSING VALUES
# ==================================================

def test_missing_values(valid_combined_dataset):
    """
    Verify that datasets containing NaN values
    are rejected.
    """

    df = valid_combined_dataset.copy()

    df.loc[0, "Flow Duration"] = np.nan

    with pytest.raises(
        ValueError,
        match="Missing values"
    ):
        validate_combined_dataset(df)


# ==================================================
# TEST 4: INFINITE VALUES
# ==================================================

def test_infinite_values(valid_combined_dataset):
    """
    Verify that positive infinity values
    are detected and rejected.
    """

    df = valid_combined_dataset.copy()

    df.loc[0, "Flow Bytes/s"] = np.inf

    with pytest.raises(
        ValueError,
        match="non-finite"
    ):
        validate_combined_dataset(df)


# ==================================================
# TEST 5: NEGATIVE FLOW DURATION
# ==================================================

def test_negative_flow_duration(valid_combined_dataset):
    """
    Verify that negative flow durations
    are rejected.
    """

    df = valid_combined_dataset.copy()

    df.loc[0, "Flow Duration"] = -100

    with pytest.raises(
        ValueError,
        match="Negative flow duration"
    ):
        validate_combined_dataset(df)


# ==================================================
# TEST 6: DUPLICATE SOURCE IDENTIFIERS
# ==================================================

def test_duplicate_source_identifiers(valid_combined_dataset):
    """
    Verify that duplicate combinations of
    SourceDataset and SourceRow are rejected.
    """

    df = valid_combined_dataset.copy()

    df.loc[1, "SourceRow"] = 0

    with pytest.raises(
        ValueError,
        match="Duplicate source"
    ):
        validate_combined_dataset(df)


# ==================================================
# TEST 7: INCORRECT RECORD COUNT
# ==================================================

def test_incorrect_row_count(valid_combined_dataset):
    """
    Verify that mismatched expected record
    counts are detected.
    """

    with pytest.raises(
        ValueError,
        match="Expected 5 rows"
    ):
        validate_combined_dataset(
            valid_combined_dataset,
            expected_rows=5,
        )


# ==================================================
# TEST 8: INCORRECT SOURCE DATASETS
# ==================================================

def test_incorrect_source_datasets(valid_combined_dataset):
    """
    Verify that unexpected or missing source
    datasets are detected.
    """

    with pytest.raises(
        ValueError,
        match="Source datasets"
    ):
        validate_combined_dataset(
            valid_combined_dataset,
            expected_sources={
                "Friday - DDoS",
            },
        )


# ==================================================
# TEST 9: MISSING ATTACK CLASS
# ==================================================

def test_missing_attack_class(valid_combined_dataset):
    """
    Verify that datasets containing only
    BENIGN traffic are rejected.
    """

    df = valid_combined_dataset.copy()

    df["Label"] = "BENIGN"

    with pytest.raises(
        ValueError,
        match="Attack class"
    ):
        validate_combined_dataset(df)


# ==================================================
# TEST 10: NON-NUMERIC FEATURE
# ==================================================

def test_non_numeric_feature(valid_combined_dataset):
    """
    Verify that the validator rejects
    non-numeric network-flow feature values.

    Explicit dtype conversion is required
    for compatibility with Pandas 3.0.
    """

    df = valid_combined_dataset.copy()

    # Convert the column to object dtype before
    # inserting a string into a numeric column.
    df["Flow Bytes/s"] = df["Flow Bytes/s"].astype(object)

    df.loc[0, "Flow Bytes/s"] = "invalid"

    with pytest.raises(
        ValueError,
        match="Non-numeric"
    ):
        validate_combined_dataset(df)


# ==================================================
# TEST 11: REPEATABILITY
# ==================================================

def test_repeatability(valid_combined_dataset):
    """
    Verify that repeated validation of the
    same dataset produces identical results.
    """

    first = validate_combined_dataset(
        valid_combined_dataset
    )

    second = validate_combined_dataset(
        valid_combined_dataset
    )

    assert first == second
