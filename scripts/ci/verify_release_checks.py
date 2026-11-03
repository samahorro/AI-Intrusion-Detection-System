"""Fail-closed deployment gate for AEGIS's GitHub Actions pipelines.

Designed for the trusted, successful Project CI push-to-main workflow_run event.
Other workflows execute independently, so poll until they finish for the exact
same commit. A branch that moves forward while waiting must never deploy stale
code. The resulting JSON is uploaded as CC8.1 change-management evidence.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

# Project CI is the workflow_run trigger and has already concluded successfully.
# Each of these workflows must separately succeed on the very same main SHA.
REQUIRED_WORKFLOWS = (
    "frontend-ci.yml",
    "integration-ci.yml",
    "ml-ci.yml",
    "soc2-access-control.yml",
    "change-management.yml",
)


def github_get(path: str, *, token: str, api_url: str = "https://api.github.com") -> dict:
    request = Request(
        f"{api_url.rstrip('/')}{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urlopen(request, timeout=20) as response:
            return json.load(response)
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"GitHub API request failed for {path.split('?')[0]}: {exc}") from exc


def select_run(runs: list[dict], *, sha: str, branch: str) -> dict | None:
    """Choose latest push workflow run, excluding unrelated PR/branch runs."""
    matching = [
        run
        for run in runs
        if run.get("head_sha") == sha
        and run.get("head_branch") == branch
        and run.get("event") == "push"
    ]
    if not matching:
        return None
    return max(matching, key=lambda r: (r.get("run_number") or 0, r.get("run_attempt") or 0))


def evaluate_gate(*, repository: str, sha: str, branch: str, fetch) -> dict:
    """One deterministic evaluation pass; no external side effects besides fetch."""
    root = f"/repos/{repository}"
    ref = fetch(f"{root}/git/ref/heads/{quote(branch, safe='')}")
    actual_sha = ref.get("object", {}).get("sha")
    results = []
    decision = "pass"

    if actual_sha != sha:
        return {
            "decision": "fail",
            "reason": "Deployment blocked: target commit is no longer the branch HEAD",
            "repository": repository,
            "branch": branch,
            "target_sha": sha,
            "current_sha": actual_sha,
            "workflows": [],
        }

    for workflow in REQUIRED_WORKFLOWS:
        query = urlencode({"head_sha": sha, "branch": branch, "event": "push", "per_page": 100})
        response = fetch(f"{root}/actions/workflows/{workflow}/runs?{query}")
        run = select_run(response.get("workflow_runs", []), sha=sha, branch=branch)
        if run is None:
            status, conclusion, url, run_id = "not_found", None, None, None
        else:
            status = run.get("status")
            conclusion = run.get("conclusion")
            url = run.get("html_url")
            run_id = run.get("id")
        if run is None or status != "completed":
            state = "waiting"
            if decision != "fail":
                decision = "wait"
        elif conclusion == "success":
            state = "passed"
        else:
            state = "failed"
            decision = "fail"
        results.append({
            "workflow": workflow,
            "state": state,
            "run_id": run_id,
            "run_url": url,
            "status": status,
            "conclusion": conclusion,
        })

    return {
        "decision": decision,
        "repository": repository,
        "branch": branch,
        "target_sha": sha,
        "current_sha": actual_sha,
        "workflows": results,
    }


def write_report(path: Path, report: dict, *, include_summary: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {**report, "evaluated_at_utc": datetime.now(timezone.utc).isoformat()}
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file and include_summary:
        with Path(summary_file).open("a", encoding="utf-8") as summary:
            summary.write("## CC8.1 deployment validation\n\n")
            summary.write(f"**Decision: {report['decision'].upper()}**  Commit: `{report.get('target_sha')}`\n\n")
            for row in report.get("workflows", []):
                summary.write(f"- `{row['workflow']}`: {row['state']} ({row['conclusion'] or row['status']})\n")
            if report.get("reason"):
                summary.write(f"\n{report['reason']}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True, help="owner/repo")
    parser.add_argument("--sha", required=True, help="Exact 40-character main commit hash")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--timeout", type=int, default=900, help="Max seconds to await checks")
    parser.add_argument("--interval", type=int, default=15, help="Poll interval seconds")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repository):
        parser.error("--repository must be owner/repo")
    if not re.fullmatch(r"[0-9a-fA-F]{40}", args.sha):
        parser.error("--sha must be a 40-character Git commit hash")
    if args.branch != "main":
        parser.error("Only the main branch is eligible for deployment")
    if args.timeout < 0 or args.interval <= 0:
        parser.error("--timeout must be >= 0 and --interval must be > 0")
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        parser.error("GITHUB_TOKEN is required for reading CI workflow results")

    deadline = time.monotonic() + args.timeout
    report = {}
    while True:
        try:
            report = evaluate_gate(
                repository=args.repository,
                sha=args.sha,
                branch=args.branch,
                fetch=lambda path: github_get(
                    path, token=token, api_url=os.environ.get("GITHUB_API_URL", "https://api.github.com")
                ),
            )
        except (RuntimeError, ValueError, KeyError) as exc:
            report = {
                "decision": "fail", "repository": args.repository,
                "branch": args.branch, "target_sha": args.sha,
                "reason": f"Deployment blocked: check verification unavailable ({exc})",
                "workflows": [],
            }
        write_report(args.output, report, include_summary=False)
        print(f"CC8.1 release gate: {report['decision']}", flush=True)
        for row in report.get("workflows", []):
            print(f"  {row['workflow']}: {row['state']}", flush=True)
        if report["decision"] == "pass":
            write_report(args.output, report)
            return 0
        if report["decision"] == "fail":
            write_report(args.output, report)
            return 1
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            report["decision"] = "fail"
            report["reason"] = "Deployment blocked: timeout waiting for required checks"
            write_report(args.output, report)
            return 1
        time.sleep(min(args.interval, remaining))


if __name__ == "__main__":
    sys.exit(main())
