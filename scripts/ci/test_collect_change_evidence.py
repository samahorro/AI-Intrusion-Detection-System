"""Offline tests for the CC8.1 change traceability manifest."""

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collect_change_evidence import make_manifest  # noqa: E402


ENV = {
    "GITHUB_REPOSITORY": "example/AEGIS",
    "GITHUB_ACTOR": "contributor",
    "GITHUB_RUN_ID": "101",
    "GITHUB_RUN_ATTEMPT": "1",
}


class ManifestTests(unittest.TestCase):
    def test_pull_request_records_author_and_head_sha(self):
        result = make_manifest(event_name="pull_request", event={"pull_request": {
            "number": 42,
            "html_url": "https://github.com/example/AEGIS/pull/42",
            "title": "Account navigation",
            "user": {"login": "contributor"},
            "head": {"sha": "abc123"},
            "base": {"ref": "main"},
            "draft": False,
        }}, env=ENV)
        self.assertEqual(result["change"]["number"], 42)
        self.assertEqual(result["change"]["head_sha"], "abc123")
        self.assertIn("not establish", result["assessment_note"])

    def test_push_records_exact_commit(self):
        result = make_manifest(event_name="push", event={
            "after": "abc123", "ref": "refs/heads/main",
        }, env=ENV)
        self.assertEqual(result["change"]["head_sha"], "abc123")
        self.assertTrue(result["workflow_url"].endswith("/actions/runs/101"))

    def test_unsupported_event_is_rejected(self):
        with self.assertRaises(ValueError):
            make_manifest(event_name="workflow_dispatch", event={}, env=ENV)


if __name__ == "__main__":
    unittest.main()
