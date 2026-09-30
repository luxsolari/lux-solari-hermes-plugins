"""Exercise the actual CLI pipeline with network/cache providers disabled."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from hannah.cli import main


class OfflineCliTests(unittest.TestCase):
    def test_json_pipeline_without_network_or_downloads(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            (repo / "main.py").write_text("print('offline fixture')\n")
            output = io.StringIO()
            with (patch("urllib.request.urlopen", side_effect=AssertionError("network forbidden")),
                  patch("hannah.cli.get_pulled_model_details", return_value={}) as local,
                  patch("hannah.cli.scan_library", return_value=[]) as library,
                  patch("hannah.cli.load_benchmark_scores", return_value={}) as benchmarks,
                  contextlib.redirect_stdout(output)):
                result = main([str(repo), "--json", "--gpu", "vram=16gb", "--ram", "32gb"])
            payload = json.loads(output.getvalue())
            self.assertEqual(result, 0)
            self.assertEqual(payload["schema"], "hannah/analysis@1")
            self.assertEqual(payload["repo"]["path"], str(repo.resolve()))
            self.assertGreater(payload["repo"]["total_lines"], 0)
            self.assertEqual(payload["hardware"]["platform"], "manual")
            self.assertEqual(payload["hardware"]["gpu_vram_gb"], 16)
            self.assertEqual(payload["discoveries"], [])
            self.assertTrue(payload["recommendations"])
            ranks = [r["rank"] for r in payload["recommendations"]]
            self.assertEqual(ranks, list(range(1, len(ranks) + 1)))
            local.assert_called_once()
            library.assert_called_once()
            benchmarks.assert_called_once()
            print("Offline real CLI verified:", payload["schema"], "P1=" + payload["recommendations"][0]["name"])

    def test_nonexistent_path_reports_failure_before_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("hannah.cli.get_pulled_model_details") as metadata, contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main([str(Path(directory) / "missing")]), 1)
            metadata.assert_not_called()


if __name__ == "__main__":
    unittest.main()
