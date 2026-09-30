#!/usr/bin/env python3
"""Regression tests for check_progress_schema.py itself.

The checker was shipped with a bug (a `warn()` call hardcoded to always
report PASS -- see CHANGELOG [Unreleased]) that only surfaced because a
Tier 2 live scenario happened to exercise that exact branch. That's too
expensive a way to catch a bug in the *checker*, which is plain
deterministic code. These fixture-driven tests pin the checker's expected
exit code (and, for FAILs, which check should fire) against known-good and
known-bad `.sage-progress.json` files under tests/fixtures/, so a future
edit to the checker gets caught by `python3 -m unittest` in seconds --
no agent, no tokens, CI-friendly.

Run: python3 tests/test_check_progress_schema.py
"""
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKER = os.path.join(HERE, "..", "scripts", "check_progress_schema.py")
FIXTURES = os.path.join(HERE, "fixtures")


def run_checker(fixture_name):
    fixture_dir = os.path.join(FIXTURES, fixture_name)
    result = subprocess.run(
        [sys.executable, CHECKER, fixture_dir],
        capture_output=True, text=True,
    )
    return result.returncode, result.stdout


class TestValidFixtures(unittest.TestCase):
    def test_valid_exits_zero(self):
        code, out = run_checker("valid")
        self.assertEqual(code, 0, out)
        self.assertNotIn("[FAIL]", out)

    def test_valid_track_complete_exits_zero_with_note(self):
        code, out = run_checker("valid-track-complete")
        self.assertEqual(code, 0, out)
        self.assertNotIn("[FAIL]", out)
        # Regression guard: this NOTE must actually render, not be silently
        # swallowed the way the pre-fix warn(label, True, ...) call was.
        self.assertIn("[NOTE]", out)
        self.assertIn("next_up is null", out)


class TestInvalidFixtures(unittest.TestCase):
    def test_bad_topic_key_fails(self):
        code, out = run_checker("invalid-topic-key")
        self.assertEqual(code, 1, out)
        self.assertIn("kebab-case", out)
        self.assertIn("[FAIL]", out)

    def test_overlapping_streaks_fails(self):
        code, out = run_checker("invalid-streak-overlap")
        self.assertEqual(code, 1, out)
        self.assertIn("mutually exclusive", out)

    def test_dangling_review_due_fails(self):
        code, out = run_checker("invalid-review-due-dangling")
        self.assertEqual(code, 1, out)
        self.assertIn("review_due entries are a subset", out)

    def test_missing_profile_fails(self):
        code, out = run_checker("invalid-missing-profile")
        self.assertEqual(code, 1, out)
        self.assertIn(".sage-profile.md", out)

    def test_malformed_json_fails(self):
        code, out = run_checker("invalid-bad-json")
        self.assertEqual(code, 1, out)
        self.assertIn("valid JSON", out)


if __name__ == "__main__":
    unittest.main()
