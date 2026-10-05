import json

import pytest

from ml.models.artifact_metadata import (
    calculate_sha256,
    create_model_metadata,
    load_model_metadata,
    save_model_metadata,
    verify_model_artifact,
)


def create_test_artifact(tmp_path):
    artifact_path = tmp_path / "ids-model.pkl"

    artifact_path.write_bytes(
        b"temporary-test-model"
    )

    return artifact_path


def test_create_model_metadata(tmp_path):
    artifact_path = create_test_artifact(
        tmp_path
    )

    metadata = create_model_metadata(
        str(artifact_path),
        version="1.0.0",
        dataset_version="cicids2017-v1",
        metrics={
            "accuracy": 0.95,
            "recall": 0.92,
        },
    )

    assert metadata["schema_version"] == 1
    assert metadata["model_version"] == "1.0.0"
    assert (
        metadata["artifact_name"]
        == "ids-model.pkl"
    )

    assert (
        metadata["dataset_version"]
        == "cicids2017-v1"
    )

    assert metadata["metrics"]["accuracy"] == 0.95
    assert metadata["metrics"]["recall"] == 0.92

    assert len(metadata["sha256"]) == 64


def test_save_and_load_model_metadata(
    tmp_path,
):
    artifact_path = create_test_artifact(
        tmp_path
    )

    metadata = create_model_metadata(
        str(artifact_path),
        version="1.0.0",
    )

    metadata_path = (
        tmp_path / "model-metadata.json"
    )

    save_model_metadata(
        metadata,
        str(metadata_path),
    )

    loaded = load_model_metadata(
        str(metadata_path)
    )

    assert loaded == metadata


def test_artifact_checksum_verification(
    tmp_path,
):
    artifact_path = create_test_artifact(
        tmp_path
    )

    metadata = create_model_metadata(
        str(artifact_path),
        version="1.0.0",
    )

    assert verify_model_artifact(
        str(artifact_path),
        metadata,
    )


def test_modified_artifact_fails_verification(
    tmp_path,
):
    artifact_path = create_test_artifact(
        tmp_path
    )

    metadata = create_model_metadata(
        str(artifact_path),
        version="1.0.0",
    )

    artifact_path.write_bytes(
        b"modified-model-artifact"
    )

    assert not verify_model_artifact(
        str(artifact_path),
        metadata,
    )


def test_missing_artifact_rejected(
    tmp_path,
):
    missing_path = (
        tmp_path / "missing.pkl"
    )

    with pytest.raises(
        FileNotFoundError,
    ):
        calculate_sha256(
            str(missing_path)
        )


def test_empty_version_rejected(
    tmp_path,
):
    artifact_path = create_test_artifact(
        tmp_path
    )

    with pytest.raises(
        ValueError,
        match="version cannot be empty",
    ):
        create_model_metadata(
            str(artifact_path),
            version="",
        )


def test_metadata_is_valid_json(
    tmp_path,
):
    artifact_path = create_test_artifact(
        tmp_path
    )

    metadata = create_model_metadata(
        str(artifact_path),
        version="2.0.0",
    )

    metadata_path = (
        tmp_path / "metadata.json"
    )

    save_model_metadata(
        metadata,
        str(metadata_path),
    )

    with metadata_path.open(
        encoding="utf-8",
    ) as metadata_file:
        parsed = json.load(
            metadata_file
        )

    assert (
        parsed["model_version"]
        == "2.0.0"
    )
    