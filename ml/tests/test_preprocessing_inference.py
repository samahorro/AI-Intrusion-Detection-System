import pickle

import pytest

from ml.models.inference import load_model, run_inference
from ml.preprocessing.flow_preprocessor import (
    REQUIRED_FEATURES,
    preprocess_flow,
)


class FakeModel:
    """
    Lightweight model used only for CI testing.

    This prevents the CI pipeline from needing to train or download
    the complete IDS model.
    """

    def predict(self, samples):
        return ["BENIGN"]


def test_preprocessing_returns_expected_feature_structure():
    flow = {
        "Flow Duration": 1500,
        "Total Fwd Packets": 10,
        "Total Backward Packets": 8,
        "Flow Bytes/s": 2500.5,
        "Flow Packets/s": 12.5,
    }

    result = preprocess_flow(flow)

    assert isinstance(result, list)
    assert len(result) == len(REQUIRED_FEATURES)

    assert result == [
        1500.0,
        10.0,
        8.0,
        2500.5,
        12.5,
    ]


def test_missing_features_are_handled():
    flow = {
        "Flow Duration": 1000,
        "Total Fwd Packets": 5,
    }

    result = preprocess_flow(flow)

    assert len(result) == len(REQUIRED_FEATURES)

    # Missing features should receive the default value.
    assert result[2] == 0.0
    assert result[3] == 0.0
    assert result[4] == 0.0


def test_none_values_are_handled():
    flow = {
        "Flow Duration": None,
        "Total Fwd Packets": 5,
        "Total Backward Packets": 3,
        "Flow Bytes/s": None,
        "Flow Packets/s": 7,
    }

    result = preprocess_flow(flow)

    assert result[0] == 0.0
    assert result[3] == 0.0


def test_invalid_numeric_value_raises_error():
    flow = {
        "Flow Duration": "invalid",
    }

    with pytest.raises(ValueError):
        preprocess_flow(flow)


def test_invalid_flow_type_raises_error():
    with pytest.raises(TypeError):
        preprocess_flow(None)


def test_model_artifact_can_be_loaded(tmp_path):
    model = FakeModel()

    model_path = tmp_path / "test_model.pkl"

    with model_path.open("wb") as model_file:
        pickle.dump(model, model_file)

    loaded_model = load_model(str(model_path))

    assert hasattr(loaded_model, "predict")


def test_missing_model_artifact_raises_error(tmp_path):
    missing_model = tmp_path / "missing_model.pkl"

    with pytest.raises(FileNotFoundError):
        load_model(str(missing_model))


def test_model_inference_completes_successfully():
    model = FakeModel()

    features = [
        1500.0,
        10.0,
        8.0,
        2500.5,
        12.5,
    ]

    result = run_inference(model, features)

    assert result["status"] == "success"
    assert result["prediction"] == "BENIGN"


def test_inference_returns_expected_output_structure():
    model = FakeModel()

    features = [0.0] * len(REQUIRED_FEATURES)

    result = run_inference(model, features)

    assert "prediction" in result
    assert "status" in result