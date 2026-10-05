import pytest

from ml.evaluation.metrics import (
    calculate_binary_metrics,
)


def test_calculate_binary_metrics_perfect_predictions():
    expected = [0, 0, 1, 1]
    predicted = [0, 0, 1, 1]

    metrics = calculate_binary_metrics(
        expected,
        predicted,
    )

    assert metrics["accuracy"] == 1.0
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1"] == 1.0


def test_calculate_binary_metrics_partial_predictions():
    expected = [0, 0, 1, 1]
    predicted = [0, 1, 1, 0]

    metrics = calculate_binary_metrics(
        expected,
        predicted,
    )

    assert metrics["accuracy"] == pytest.approx(0.5)
    assert metrics["precision"] == pytest.approx(0.5)
    assert metrics["recall"] == pytest.approx(0.5)
    assert metrics["f1"] == pytest.approx(0.5)


def test_calculate_binary_metrics_supports_string_labels():
    expected = [
        "BENIGN",
        "ATTACK",
        "ATTACK",
    ]

    predicted = [
        "BENIGN",
        "ATTACK",
        "BENIGN",
    ]

    metrics = calculate_binary_metrics(
        expected,
        predicted,
        positive_label="ATTACK",
    )

    assert metrics["accuracy"] == pytest.approx(
        2 / 3
    )

    assert metrics["precision"] == pytest.approx(
        1.0
    )

    assert metrics["recall"] == pytest.approx(
        0.5
    )

    assert metrics["f1"] == pytest.approx(
        2 / 3
    )


def test_mismatched_label_lengths_rejected():
    with pytest.raises(
        ValueError,
        match="same length",
    ):
        calculate_binary_metrics(
            [0, 1],
            [0],
        )


def test_empty_labels_rejected():
    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        calculate_binary_metrics(
            [],
            [],
        )