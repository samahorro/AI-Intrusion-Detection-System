import hashlib
import json
from pathlib import Path
from typing import Any


def calculate_sha256(
    artifact_path: str,
) -> str:
    """
    Calculate the SHA-256 checksum of a model artifact.
    """

    path = Path(artifact_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Model artifact not found: {artifact_path}"
        )

    digest = hashlib.sha256()

    with path.open("rb") as artifact_file:
        for chunk in iter(
            lambda: artifact_file.read(8192),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def create_model_metadata(
    artifact_path: str,
    version: str,
    dataset_version: str | None = None,
    metrics: dict[str, float] | None = None,
) -> dict[str, Any]:
    """
    Create metadata describing a versioned model artifact.
    """

    if not version.strip():
        raise ValueError(
            "Model version cannot be empty."
        )

    path = Path(artifact_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Model artifact not found: {artifact_path}"
        )

    return {
        "schema_version": 1,
        "model_version": version,
        "artifact_name": path.name,
        "sha256": calculate_sha256(
            artifact_path
        ),
        "dataset_version": dataset_version,
        "metrics": metrics or {},
    }


def save_model_metadata(
    metadata: dict[str, Any],
    metadata_path: str,
) -> None:
    """
    Save model metadata as JSON.
    """

    path = Path(metadata_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as metadata_file:
        json.dump(
            metadata,
            metadata_file,
            indent=2,
            sort_keys=True,
        )


def load_model_metadata(
    metadata_path: str,
) -> dict[str, Any]:
    """
    Load model metadata from JSON.
    """

    path = Path(metadata_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Model metadata not found: {metadata_path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as metadata_file:
        return json.load(metadata_file)


def verify_model_artifact(
    artifact_path: str,
    metadata: dict[str, Any],
) -> bool:
    """
    Verify that a model artifact matches its recorded checksum.
    """

    expected_checksum = metadata.get(
        "sha256"
    )

    if not expected_checksum:
        raise ValueError(
            "Model metadata does not contain a SHA-256 checksum."
        )

    actual_checksum = calculate_sha256(
        artifact_path
    )

    return actual_checksum == expected_checksum