"""Record traceable GitHub PR / push metadata without claiming review approval.

This creates *supporting* CC8.1 evidence; a passing run alone does not show
branch protection, reviewer approval, or deployment authorization.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def make_manifest(*, event_name: str, event: dict, env: dict) -> dict:
    repo = env.get("GITHUB_REPOSITORY") or event.get("repository", {}).get("full_name")
    context = {
        "control": "SOC 2 CC8.1 - Change Management",
        "evidence_type": "automated_change_context",
        "assessment_note": "Does not establish reviewer approval or branch protection enforcement",
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository": repo,
        "event": event_name,
        "actor": env.get("GITHUB_ACTOR"),
        "workflow_run_id": env.get("GITHUB_RUN_ID"),
        "workflow_run_attempt": env.get("GITHUB_RUN_ATTEMPT"),
        "workflow_url": (
            f"{env.get('GITHUB_SERVER_URL', 'https://github.com')}/{repo}/actions/runs/"
            f"{env.get('GITHUB_RUN_ID')}" if repo and env.get("GITHUB_RUN_ID") else None
        ),
    }
    if event_name == "pull_request":
        pr = event.get("pull_request") or {}
        context["change"] = {
            "number": pr.get("number"),
            "url": pr.get("html_url"),
            "title": pr.get("title"),
            "author": (pr.get("user") or {}).get("login"),
            "head_sha": (pr.get("head") or {}).get("sha"),
            "base_branch": (pr.get("base") or {}).get("ref"),
            "draft": pr.get("draft"),
            "merged": pr.get("merged", False),
        }
    elif event_name == "push":
        context["change"] = {
            "head_sha": event.get("after"),
            "branch_ref": event.get("ref"),
            "compare_url": event.get("compare"),
        }
    else:
        raise ValueError(f"Unsupported event: {event_name}")
    return context


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        parser.error("GITHUB_EVENT_PATH is required")
    event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    manifest = make_manifest(event_name=os.environ.get("GITHUB_EVENT_NAME", ""), event=event, env=os.environ)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with Path(summary).open("a", encoding="utf-8") as f:
            f.write("## CC8.1 change traceability\n\n")
            f.write(f"- Event: **{manifest['event']}**\n")
            f.write(f"- Change SHA: `{manifest['change'].get('head_sha')}`\n")
            f.write("- Review/branch rules: **not assessed by this job**\n")


if __name__ == "__main__":
    main()
