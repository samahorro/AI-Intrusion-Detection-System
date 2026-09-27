import pickle
from pathlib import Path
from typing import Any, Dict, List


def load_model(model_path: str) -> Any:
    """
    Load a serialized model artifact from disk.
    """

    path = Path(model_path)

    if not path.exists():
        raise FileNotFoundError(f"Model artifact not found: {model_path}")

    with path.open("rb") as model_file:
        return pickle.load(model_file)


def run_inference(model: Any, features: List[float]) -> Dict[str, Any]:
    """
    Run model inference against one preprocessed feature vector.
    """

    if not hasattr(model, "predict"):
        raise TypeError("Model must provide a predict() method")

    prediction = model.predict([features])

    if len(prediction) == 0:
        raise ValueError("Model returned no predictions")

    predicted_value = prediction[0]

    # Convert NumPy scalar values to normal Python types when necessary.
    if hasattr(predicted_value, "item"):
        predicted_value = predicted_value.item()

    return {
        "prediction": predicted_value,
        "status": "success",
    }