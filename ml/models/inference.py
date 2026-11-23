
import math
from pathlib import Path
from typing import Any, Dict, List

import joblib


def load_model(model_path: str) -> Any:
    """
    Load a trusted Joblib model artifact from disk.
    """
    path = Path(model_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Model artifact not found: {model_path}"
        )

    return joblib.load(path)


def _is_attack_class(label: Any) -> bool:
    """
    Identify supported binary attack labels.
    """
    if hasattr(label, "item"):
        label = label.item()

    if isinstance(label, str):
        return label.strip().lower() in {
            "1",
            "attack",
            "malicious",
        }

    return label == 1


def run_inference(
    model: Any,
    features: List[float],
) -> Dict[str, Any]:
    """
    Run inference against one preprocessed feature vector.

    When supported, include the probability associated
    with the ATTACK class.
    """

    if not hasattr(model, "predict"):
        raise TypeError(
            "Model must provide a predict() method"
        )

    prediction = model.predict([features])

    if len(prediction) == 0:
        raise ValueError("Model returned no predictions")

    predicted_value = prediction[0]

    if hasattr(predicted_value, "item"):
        predicted_value = predicted_value.item()

    result = {
        "prediction": predicted_value,
        "status": "success",
    }

    # Preserve compatibility with prediction-only models.
    if not hasattr(model, "predict_proba"):
        return result

    # Probability columns must be mapped using model.classes_.
    if not hasattr(model, "classes_"):
        return result

    attack_indices = [
        index
        for index, label in enumerate(model.classes_)
        if _is_attack_class(label)
    ]

    # Do not guess when the attack class is missing or ambiguous.
    if len(attack_indices) != 1:
        return result

    probabilities = model.predict_proba([features])

    if len(probabilities) != 1:
        raise ValueError(
            "Model returned an unexpected probability shape"
        )

    attack_index = attack_indices[0]

    try:
        attack_probability = float(
            probabilities[0][attack_index]
        )
    except (IndexError, TypeError, ValueError) as exc:
        raise ValueError(
            "Model returned invalid attack probabilities"
        ) from exc

    if (
        not math.isfinite(attack_probability)
        or not 0.0 <= attack_probability <= 1.0
    ):
        raise ValueError(
            "Attack probability must be finite and between 0 and 1"
        )

    result["attack_probability"] = attack_probability

    return result
