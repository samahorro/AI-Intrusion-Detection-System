"""KAN-126 CI tests: synthetic data only; no CICIDS2017 CSVs required.

Run: python -m pytest ml/tests/test_feature_engineering_ci.py -v
"""

import numpy as np
import pandas as pd
import pytest

from ml.preprocessing.feature_engineering import (
    FEATURES, TARGET, assign_splits, prepare_model_records, split_xy,
)


@pytest.fixture
def records():
    return pd.DataFrame({
        "Flow Duration": [100, 200, 300, 100, 400, 500],
        "Total Fwd Packets": [10, 20, 30, 10, 40, 50],
        "Total Backward Packets": [1, 2, 3, 1, 4, 5],
        "Flow Bytes/s": [10.5, 20.5, 30.5, 10.5, 40.5, 50.5],
        "Flow Packets/s": [2.5, 3.5, 4.5, 2.5, 5.5, 6.5],
        "SourceDataset": ["Monday"] * 3 + ["Tuesday"] * 3,
        "SourceRow": [0, 1, 2, 0, 1, 2],
        "Label": ["BENIGN", "DoS Hulk", "BENIGN", "BENIGN", "Bot", "BENIGN"],
    })


def test_feature_order(records):
    result = prepare_model_records(records)
    assert list(result.columns[:5]) == FEATURES


def test_binary_encoding(records):
    result = prepare_model_records(records)
    assert result[TARGET].tolist() == [0, 1, 0, 0, 1, 0]


def test_label_whitespace_is_stripped(records):
    records.loc[0, "Label"] = " BENIGN "
    result = prepare_model_records(records)
    assert result.loc[0, "Label"] == "BENIGN"
    assert result.loc[0, TARGET] == 0


def test_nonfinite_rows_excluded(records):
    records.loc[0, "Flow Bytes/s"] = np.inf
    records.loc[1, "Flow Packets/s"] = np.nan
    result = prepare_model_records(records)
    assert len(result) == 4
    assert np.isfinite(result[FEATURES].to_numpy(dtype="float64")).all()


def test_negative_feature_rows_excluded(records):
    records.loc[0, "Flow Duration"] = -1
    result = prepare_model_records(records)
    assert len(result) == 5
    assert (result[FEATURES] >= 0).all().all()


def test_zero_values_retained(records):
    records.loc[0, "Flow Duration"] = 0
    result = prepare_model_records(records)
    assert len(result) == 6
    assert result.loc[0, "Flow Duration"] == 0


def test_missing_feature_raises(records):
    with pytest.raises(ValueError, match="Missing columns"):
        prepare_model_records(records.drop(columns=[FEATURES[0]]))


def test_nonnumeric_feature_raises(records):
    records["Flow Bytes/s"] = records["Flow Bytes/s"].astype(object)
    records.loc[0, "Flow Bytes/s"] = "invalid"
    with pytest.raises(ValueError, match="numeric"):
        prepare_model_records(records)


def test_does_not_mutate_input(records):
    original = records.copy(deep=True)
    prepare_model_records(records)
    pd.testing.assert_frame_equal(records, original)


def test_same_features_same_signature_and_split(records):
    result = prepare_model_records(records)
    assert result.loc[0, "FeatureSignature"] == result.loc[3, "FeatureSignature"]
    assert result.loc[0, "Split"] == result.loc[3, "Split"]


def test_no_feature_signature_crosses_partitions(records):
    result = prepare_model_records(records)
    groups = result.groupby("FeatureSignature")["Split"].nunique()
    assert groups.eq(1).all()


def test_split_assignment_deterministic(records):
    first = prepare_model_records(records)
    second = prepare_model_records(records)
    pd.testing.assert_frame_equal(first, second)


def test_bucket_boundaries():
    # Check the exact assignment logic against an independent implementation
    # of Notebook 10's 64-bit mixing, including threshold boundaries.
    signatures = np.arange(10000, dtype=np.uint64)
    keys = signatures ^ np.uint64(20261010)
    keys ^= keys >> np.uint64(30)
    keys *= np.uint64(0xbf58476d1ce4e5b9)
    keys ^= keys >> np.uint64(27)
    keys *= np.uint64(0x94d049bb133111eb)
    keys ^= keys >> np.uint64(31)
    buckets = keys % np.uint64(100)
    expected = np.select([buckets < 70, buckets < 85], ["train", "validation"], default="test")
    np.testing.assert_array_equal(assign_splits(signatures), expected)
    assert set(expected) == {"train", "validation", "test"}


def test_xy_excludes_labels_and_source_metadata(records):
    result = prepare_model_records(records)
    x, y = split_xy(result)
    assert list(x.columns) == FEATURES
    assert x.shape == (len(result), 5)
    assert y.name == TARGET
    assert x.dtypes.eq("float32").all()
    assert y.dtype == np.dtype("int8")
    assert not {"Label", "SourceDataset", "SourceRow", "BinaryLabel", "Split", "FeatureSignature"}.intersection(x.columns)


def test_xy_matches_binary_labels(records):
    result = prepare_model_records(records)
    _, y = split_xy(result)
    assert y.tolist() == (result["Label"] != "BENIGN").astype("int8").tolist()


def test_model_input_is_finite(records):
    result = prepare_model_records(records)
    x, _ = split_xy(result)
    assert np.isfinite(x.to_numpy()).all()


def test_metadata_not_used_to_assign_split(records):
    baseline = prepare_model_records(records)
    changed = records.copy()
    changed["SourceDataset"] = "Another day"
    changed["SourceRow"] += 100
    changed["Label"] = changed["Label"].map(lambda x: "BENIGN" if x != "BENIGN" else "Bot")
    updated = prepare_model_records(changed)
    np.testing.assert_array_equal(baseline["Split"].to_numpy(), updated["Split"].to_numpy())
    np.testing.assert_array_equal(baseline["FeatureSignature"].to_numpy(), updated["FeatureSignature"].to_numpy())


def test_missing_metadata_rejected(records):
    records.loc[0, "SourceDataset"] = None
    with pytest.raises(ValueError, match="Missing source"):
        prepare_model_records(records)
