"""Verify the flattened snapshot path without fetching upstream."""
import contextlib
import importlib.util
import io
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("drift", ROOT / "scripts/check_framework_drift.py")
assert spec is not None and spec.loader is not None
drift = importlib.util.module_from_spec(spec)
spec.loader.exec_module(drift)


class DriftTests(unittest.TestCase):
    def test_snapshot_path_and_clean_offline(self):
        expected = ROOT / "references/three-axes-upstream-snapshot.md"
        self.assertEqual(drift.SNAPSHOT_PATH, expected)
        self.assertTrue(expected.is_file())
        with patch.object(drift, "fetch_upstream", return_value=expected.read_text(encoding="utf-8")), patch.object(drift.sys, "stdout", io.TextIOWrapper(io.BytesIO(), encoding="utf-8")):
            self.assertEqual(drift.main(), 0)

    def test_network_failure_is_not_clean(self):
        with patch.object(drift, "fetch_upstream", side_effect=OSError("offline")), patch.object(drift.sys, "stdout", io.TextIOWrapper(io.BytesIO(), encoding="utf-8")):
            self.assertEqual(drift.main(), 1)


if __name__ == "__main__":
    unittest.main()
