from typing import Any, Sequence


def calculate_binary_metrics(
    expected: Sequence[Any],
    predicted: Sequence[Any],
    positive_label: Any = 1,
) -> dict[str, float]:
    """
    Calculate binary classification metrics without external
    machine-learning dependencies.
    """

    if len(expected) != len(predicted):
        raise ValueError(
            "Expected and predicted labels must have the same length."
        )

    if len(expected) == 0:
        raise ValueError(
            "Evaluation labels cannot be empty."
        )

    true_positive = 0
    true_negative = 0
    false_positive = 0
    false_negative = 0

    for expected_label, predicted_label in zip(
        expected,
        predicted,
    ):
        expected_positive = (
            expected_label == positive_label
        )
        predicted_positive = (
            predicted_label == positive_label
        )

        if expected_positive and predicted_positive:
            true_positive += 1
        elif not expected_positive and not predicted_positive:
            true_negative += 1
        elif not expected_positive and predicted_positive:
            false_positive += 1
        else:
            false_negative += 1

    total = len(expected)

    accuracy = (
        true_positive + true_negative
    ) / total

    precision_denominator = (
        true_positive + false_positive
    )

    precision = (
        true_positive / precision_denominator
        if precision_denominator
        else 0.0
    )

    recall_denominator = (
        true_positive + false_negative
    )

    recall = (
        true_positive / recall_denominator
        if recall_denominator
        else 0.0
    )

    f1_denominator = precision + recall

    f1 = (
        2 * precision * recall / f1_denominator
        if f1_denominator
        else 0.0
    )

    return {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
    }