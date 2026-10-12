import re
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import create_app


def read_ci_workflow() -> str:
    workflow_path = Path(
        ".github/workflows/ci.yml"
    )

    assert workflow_path.exists()

    return workflow_path.read_text(
        encoding="utf-8"
    )


def test_project_ci_contains_required_backend_checks():
    workflow = read_ci_workflow()

    assert re.search(
        r"python-version:\s*[\"']?3\.12[\"']?",
        workflow,
    )

    assert "python -m ruff check backend" in workflow

    assert (
        "python -m pytest backend/tests"
        in workflow
    )

    assert "--cov=backend/app" in workflow

    assert "--cov-fail-under=80" in workflow


def test_ci_runs_for_pull_requests_to_main():
    workflow = read_ci_workflow()

    assert "pull_request:" in workflow

    assert re.search(
        r"pull_request:\s*\n"
        r"\s*branches:\s*\n"
        r"\s*-\s+main",
        workflow,
    )


def test_ci_runs_for_pushes_to_main():
    workflow = read_ci_workflow()

    assert "push:" in workflow

    assert re.search(
        r"push:\s*\n"
        r"\s*branches:\s*\n"
        r"\s*-\s+main",
        workflow,
    )


def test_backend_import_smoke_check_is_in_ci():
    workflow = read_ci_workflow()

    assert (
        "from backend.app.main import app"
        in workflow
    )


def test_custom_frontend_origin_is_applied(
    monkeypatch,
):
    monkeypatch.setenv(
        "FRONTEND_ORIGIN",
        "https://example.test",
    )

    application = create_app(
        initialize_database=False,
    )

    with TestClient(application) as client:
        response = client.get(
            "/health",
            headers={
                "Origin": "https://example.test",
            },
        )

    assert response.status_code == 200

    assert (
        response.headers[
            "access-control-allow-origin"
        ]
        == "https://example.test"
    )


def test_unapproved_origin_is_not_allowed(
    monkeypatch,
):
    monkeypatch.setenv(
        "FRONTEND_ORIGIN",
        "https://example.test",
    )

    application = create_app(
        initialize_database=False,
    )

    with TestClient(application) as client:
        response = client.get(
            "/health",
            headers={
                "Origin": "https://not-allowed.test",
            },
        )

    assert response.status_code == 200

    assert (
        response.headers.get(
            "access-control-allow-origin"
        )
        is None
    )