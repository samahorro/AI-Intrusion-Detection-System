import pytest
from fastapi import HTTPException

from backend.app.detection import routes


def test_get_detection_model_handles_missing_model_file(
    monkeypatch,
):
    monkeypatch.setenv(
        "MODEL_PATH",
        "missing-model.pkl",
    )

    def raise_missing_file(path):
        raise FileNotFoundError(path)

    monkeypatch.setattr(
        routes,
        "load_model",
        raise_missing_file,
    )

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        routes.get_detection_model()

    assert exc_info.value.status_code == 503
    assert (
        exc_info.value.detail
        == "Detection model is unavailable."
    )


@pytest.mark.parametrize(
    "prediction",
    [
        "0",
        "false",
        "normal",
        "benign",
        " NORMAL ",
        "False",
    ],
)
def test_prediction_is_attack_rejects_normal_strings(
    prediction,
):
    assert (
        routes.prediction_is_attack(
            prediction
        )
        is False
    )


@pytest.mark.parametrize(
    "prediction",
    [
        "1",
        "attack",
        "malicious",
        "intrusion",
        " ATTACK ",
    ],
)
def test_prediction_is_attack_accepts_attack_strings(
    prediction,
):
    assert (
        routes.prediction_is_attack(
            prediction
        )
        is True
    )


def test_prediction_is_attack_handles_non_strings():
    assert routes.prediction_is_attack(1) is True
    assert routes.prediction_is_attack(0) is False
    assert routes.prediction_is_attack(True) is True
    assert routes.prediction_is_attack(False) is False