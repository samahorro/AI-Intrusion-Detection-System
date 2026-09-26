from typing import Any, Dict, List


# Initial lightweight feature contract used for CI validation.
# This can be expanded later when the final trained model feature set is established.
REQUIRED_FEATURES = [
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Flow Bytes/s",
    "Flow Packets/s",
]


def preprocess_flow(flow: Dict[str, Any]) -> List[float]:
    """
    Convert a network-flow dictionary into the ordered numeric feature
    vector expected by the inference layer.

    Missing or None values are replaced with 0.0 so that CI can verify
    predictable preprocessing behavior.
    """

    if not isinstance(flow, dict):
        raise TypeError("flow must be a dictionary")

    processed_features = []

    for feature in REQUIRED_FEATURES:
        value = flow.get(feature, 0.0)

        if value is None:
            value = 0.0

        try:
            processed_features.append(float(value))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Feature '{feature}' must contain a numeric value"
            ) from exc

    return processed_features