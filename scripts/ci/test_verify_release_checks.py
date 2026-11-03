"""Offline regression tests for the CC8.1 deployment gate."""

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_release_checks import REQUIRED_WORKFLOWS, evaluate_gate, select_run  # noqa: E402


SHA = "a" * 40
OTHER_SHA = "b" * 40
REPO = "example/AEGIS"


def run_info(sha=SHA, branch="main", event="push", status="completed", conclusion="success", attempt=1):
    return {
        "head_sha": sha,
        "head_branch": branch,
        "event": event,
        "status": status,
        "conclusion": conclusion,
        "run_number": 12,
        "run_attempt": attempt,
        "id": 77,
        "html_url": "https://github.com/example/AEGIS/actions/runs/77",
    }


def make_fetcher(*, head=SHA, overrides=None):
    overrides = overrides or {}

    def fetch(path):
        if path.endswith("/git/ref/heads/main"):
            return {"object": {"sha": head}}
        for filename in REQUIRED_WORKFLOWS:
            if f"/workflows/{filename}/runs?" in path:
                return {"workflow_runs": overrides.get(filename, [run_info()])}
        raise AssertionError(f"Unexpected API request: {path}")

    return fetch


class ReleaseGateTests(unittest.TestCase):
    def check(self, **kwargs):
        return evaluate_gate(repository=REPO, sha=SHA, branch="main", fetch=make_fetcher(**kwargs))

    def test_all_required_workflows_succeed(self):
        report = self.check()
        self.assertEqual(report["decision"], "pass")
        self.assertEqual(len(report["workflows"]), len(REQUIRED_WORKFLOWS))
        self.assertTrue(all(r["state"] == "passed" for r in report["workflows"]))

    def test_missing_workflow_blocks_deployment(self):
        report = self.check(overrides={"integration-ci.yml": []})
        self.assertEqual(report["decision"], "wait")

    def test_running_workflow_blocks_deployment(self):
        report = self.check(overrides={"ml-ci.yml": [run_info(status="in_progress", conclusion=None)]})
        self.assertEqual(report["decision"], "wait")

    def test_failed_workflow_blocks_deployment(self):
        report = self.check(overrides={"frontend-ci.yml": [run_info(conclusion="failure")]})
        self.assertEqual(report["decision"], "fail")

    def test_skipped_workflow_does_not_count_as_success(self):
        report = self.check(overrides={"ml-ci.yml": [run_info(conclusion="skipped")]})
        self.assertEqual(report["decision"], "fail")

    def test_stale_commit_blocks_deployment(self):
        report = self.check(head=OTHER_SHA)
        self.assertEqual(report["decision"], "fail")
        self.assertIn("no longer", report["reason"])

    def test_pr_and_other_sha_cannot_satisfy_check(self):
        report = self.check(overrides={"integration-ci.yml": [
            run_info(event="pull_request"), run_info(sha=OTHER_SHA), run_info(branch="feature"),
        ]})
        self.assertEqual(report["decision"], "wait")

    def test_newest_rerun_is_used(self):
        selected = select_run([run_info(attempt=1), run_info(attempt=2, conclusion="failure")], sha=SHA, branch="main")
        self.assertEqual(selected["run_attempt"], 2)
        report = self.check(overrides={"ml-ci.yml": [run_info(attempt=1), run_info(attempt=2, conclusion="failure")]})
        self.assertEqual(report["decision"], "fail")

    def test_fail_closed_on_api_error(self):
        def fetch(_path):
            raise RuntimeError("GitHub API unavailable")
        with self.assertRaises(RuntimeError):
            evaluate_gate(repository=REPO, sha=SHA, branch="main", fetch=fetch)


if __name__ == "__main__":
    unittest.main()
