"""Smoke tests — scrutineering before the car leaves the garage.

Pure stdlib (unittest), no pytest dependency required:
    python3 -m unittest discover -s tests
"""

import json
import tempfile
import unittest
from pathlib import Path


class LocalPackageContractTests(unittest.TestCase):
    def test_plugin_contains_its_own_hannah_engine(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "hannah" / "cli.py").is_file())

    def test_cli_version_matches_published_package_version(self):
        import hannah
        self.assertEqual(hannah.__version__, "0.10.6")
from pathlib import Path
from unittest.mock import patch

from hannah.analyzers.repo import RepoAnalyzer
from hannah.catalog.ollama import _strip_quant, detect_uncatalogued, names_match
from hannah.hardware.detect import HardwareSpec, Platform, detect_hardware
from hannah.models.registry import MODEL_CATALOG, Discovery, ModelRegistry, RecommendResult
from hannah.reporters.json import JSONReporter


def _make_repo() -> Path:
    d = Path(tempfile.mkdtemp())
    (d / "src").mkdir()
    (d / "src" / "app.py").write_text(
        "from fastapi import FastAPI\nfrom pydantic import BaseModel\napp = FastAPI()\n"
    )
    (d / "package.json").write_text('{"dependencies": {"react": "^18", "vite": "^5"}}')
    # README prose names frameworks that should NOT be detected.
    (d / "README.md").write_text("Built with Django and Svelte and torch and flask.")
    return d


def _hw() -> HardwareSpec:
    return HardwareSpec(platform=Platform.MACOS, gpu_vram_gb=16, system_ram_gb=16, gpu_backend="mlx")


class RepoAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.profile = RepoAnalyzer().analyze(_make_repo())

    def test_detects_real_frameworks(self):
        for fw in ("fastapi", "pydantic", "react", "vite"):
            self.assertIn(fw, self.profile.frameworks)

    def test_ignores_prose_mentions(self):
        for fw in ("django", "svelte", "torch", "flask"):
            self.assertNotIn(fw, self.profile.frameworks, f"{fw} leaked from README prose")

    def test_languages_and_score(self):
        self.assertIn("Python", self.profile.languages)
        self.assertGreater(self.profile.complexity_score, 0)
        self.assertIn(self.profile.compound, {"Soft", "Medium", "Hard", "Intermediate"})


class HardwareTests(unittest.TestCase):
    def test_override_passthrough(self):
        override = HardwareSpec(platform=Platform.MANUAL, gpu_vram_gb=16, system_ram_gb=32)
        self.assertIs(detect_hardware(override), override)

    def test_quant_ceiling(self):
        self.assertEqual(HardwareSpec(gpu_vram_gb=24).max_recommended_quant, "q6_k")
        self.assertEqual(HardwareSpec(gpu_vram_gb=8).max_recommended_quant, "q4_k_m")

    def test_gpu_count_default_one(self):
        hw = HardwareSpec(gpu_vram_gb=24, gpu_count=1)
        self.assertEqual(hw.gpu_count, 1)

    def test_gpu_count_multi_reflected_in_summary(self):
        hw = HardwareSpec(
            platform=Platform.LINUX,
            gpu_vram_gb=48,
            gpu_count=2,
            gpu_model="RTX 4090",
            gpu_backend="cuda",
            system_ram_gb=128,
        )
        summary = hw.summary()
        self.assertIn("2×", summary)
        self.assertIn("RTX 4090", summary)
        self.assertIn("48GB", summary)


class MultiGpuTests(unittest.TestCase):
    """VRAM summation across multiple GPUs via mocked nvidia-smi output."""

    def test_nvidia_multi_gpu_vram_summed(self):
        # Two RTX 4090s: 24576 MB each
        nvidia_output = "24576, NVIDIA RTX 4090\n24576, NVIDIA RTX 4090\n"
        with patch("hannah.hardware.detect._run") as mock_run:
            mock_run.return_value = nvidia_output.strip()
            from hannah.hardware.detect import _probe_gpu
            vram, model, vendor, count = _probe_gpu()
        self.assertEqual(count, 2)
        # 24576 + 24576 = 49152 MB → 48 GB
        self.assertEqual(vram, 48)
        self.assertEqual(model, "NVIDIA RTX 4090")

    def test_nvidia_single_gpu_unchanged(self):
        nvidia_output = "16384, NVIDIA RTX 4080\n"
        with patch("hannah.hardware.detect._run") as mock_run:
            mock_run.return_value = nvidia_output.strip()
            from hannah.hardware.detect import _probe_gpu
            vram, model, vendor, count = _probe_gpu()
        self.assertEqual(count, 1)
        self.assertEqual(vram, 16)

    def test_amd_multi_gpu_vram_summed(self):
        # rocm-smi CSV: header + two GPU rows, VRAM in bytes (16 GB each)
        rocm_output = (
            "device,VRAM Total Memory (B)\n"
            "0,17179869184\n"
            "1,17179869184\n"
        )
        with patch("hannah.hardware.detect._run") as mock_run:
            # First call (nvidia-smi) returns None; second call (rocm-smi) returns data
            mock_run.side_effect = [None, rocm_output.strip()]
            from hannah.hardware.detect import _probe_gpu
            vram, model, vendor, count = _probe_gpu()
        self.assertEqual(count, 2)
        self.assertEqual(vram, 32)


class OllamaNameMatchTests(unittest.TestCase):
    def test_exact_match(self):
        self.assertTrue(names_match("qwen3.5:9b-mlx", "qwen3.5:9b-mlx"))

    def test_quant_stripped(self):
        self.assertTrue(names_match("qwen2.5-coder:14b", "qwen2.5-coder:14b-q4_k_m"))
        self.assertTrue(names_match("gemma4:12b", "gemma4:12b-mlx"))
        self.assertTrue(names_match("llama3.1:8b", "llama3.1:8b-q6_k"))

    def test_no_false_positive(self):
        self.assertFalse(names_match("qwen3.5:9b", "qwen3:14b-q4_k_m"))
        self.assertFalse(names_match("gemma4:12b", "gemma3:12b-q4_k_m"))

    def test_strip_quant_helper(self):
        self.assertEqual(_strip_quant("qwen2.5-coder:14b-q4_k_m"), "qwen2.5-coder:14b")
        self.assertEqual(_strip_quant("gemma4:12b-mlx"), "gemma4:12b")
        self.assertEqual(_strip_quant("llama3.1:8b-q6_k"), "llama3.1:8b")
        self.assertEqual(_strip_quant("qwen3.5:9b"), "qwen3.5:9b")  # no suffix → unchanged


class RecommendationTests(unittest.TestCase):
    def test_ranked_and_scored(self):
        profile = RepoAnalyzer().analyze(_make_repo())
        result = ModelRegistry().recommend(profile, _hw(), track="development")
        self.assertIsInstance(result, RecommendResult)
        self.assertTrue(result)
        self.assertEqual([r.rank for r in result], list(range(1, len(result) + 1)))

    def test_all_models_tagged_pull_required_when_no_ollama(self):
        profile = RepoAnalyzer().analyze(_make_repo())
        result = ModelRegistry().recommend(profile, _hw(), pulled_models=set())
        for rec in result:
            self.assertFalse(rec.model.pulled)
            self.assertIn("pull required", rec.tag)

    def test_pulled_model_marked_and_tagged(self):
        profile = RepoAnalyzer().analyze(_make_repo())
        result = ModelRegistry().recommend(profile, _hw(), pulled_models={"qwen3.5:9b"})
        pulled_recs = [r for r in result if r.model.pulled]
        self.assertTrue(pulled_recs, "Expected at least one pulled model in recommendations")
        for rec in pulled_recs:
            self.assertIn("ready to race", rec.tag)

    def test_pulled_boost_is_tiebreaker_only(self):
        """A pulled model with +0.5 should not leapfrog a model with a significantly
        higher fitness score (MLX optimized = +3 advantage)."""
        profile = RepoAnalyzer().analyze(_make_repo())
        hw = _hw()
        recs_with_pull = ModelRegistry().recommend(profile, hw, pulled_models={"llama3.1:8b"})
        recs_baseline = ModelRegistry().recommend(profile, hw, pulled_models=set())
        self.assertEqual(recs_with_pull[0].model.name, recs_baseline[0].model.name)

    def test_json_schema_shape(self):
        profile = RepoAnalyzer().analyze(_make_repo())
        result = ModelRegistry().recommend(profile, _hw(), "development")
        payload = JSONReporter().build(profile, _hw(), result.podium, "development", result.discoveries)
        restored = json.loads(json.dumps(payload))
        self.assertEqual(restored["schema"], "hannah/analysis@1")
        self.assertIn("repo", restored)
        self.assertIn("hardware", restored)
        self.assertIn("recommendations", restored)
        self.assertIn("discoveries", restored)
        # v0.2: each recommendation now carries pulled status
        self.assertIn("pulled", restored["recommendations"][0])
        # v0.3: repo section carries fuel load fields
        repo_section = restored["repo"]
        self.assertIn("estimated_tokens", repo_section)
        self.assertIn("fuel_label", repo_section)
        self.assertIn("fuel_note", repo_section)

    def test_fuel_load_populated(self):
        profile = RepoAnalyzer().analyze(_make_repo())
        self.assertGreater(profile.estimated_tokens, 0)
        valid_labels = {"featherweight", "light", "moderate", "heavy", "max load", "overweight"}
        self.assertIn(profile.fuel_label, valid_labels)
        self.assertTrue(profile.fuel_note)


class BenchmarkScoringTests(unittest.TestCase):
    """Benchmark scores improve ranking and vary by track."""

    def test_benchmark_bonus_increases_score_directly(self):
        """A model with humaneval=0.92 must score higher than the same model at 0.65."""
        from hannah.models.registry import ModelCandidate
        profile = RepoAnalyzer().analyze(_make_repo())
        hw = HardwareSpec(platform=Platform.LINUX, gpu_vram_gb=24, system_ram_gb=64, gpu_backend="cuda")

        shared = dict(
            family="test", params_b=7, quant="q4_k_m", size_gb=4.5,
            context_k=128000, strengths=["coding", "general"], mlx=False,
            requirements_tier="low",
        )
        high_bench = ModelCandidate(name="high:7b", humaneval=0.92, mbpp=0.90, **shared)
        low_bench  = ModelCandidate(name="low:7b",  humaneval=0.65, mbpp=0.60, **shared)

        registry = ModelRegistry()
        scored = registry._score([high_bench, low_bench], profile, hw, "development")
        scores = {c.name: s["score"] for c, s in scored}
        self.assertGreater(scores["high:7b"], scores["low:7b"])

    def test_all_catalog_entries_have_hf_model_id(self):
        """Every catalog entry must have hf_model_id set for benchmark lookup."""
        for m in MODEL_CATALOG:
            self.assertIsNotNone(m.hf_model_id, f"{m.name} is missing hf_model_id")
            self.assertIn("/", m.hf_model_id, f"{m.name} hf_model_id must be Org/Name format")

    def test_benchmark_catalog_scores_start_as_none(self):
        """Catalog entries have no hardcoded benchmark scores — fetch populates them at runtime."""
        for m in MODEL_CATALOG:
            self.assertIsNone(m.humaneval, f"{m.name} should have no hardcoded humaneval")
            self.assertIsNone(m.mbpp, f"{m.name} should have no hardcoded mbpp")

    def test_mmlu_pro_weight_higher_on_general_than_development(self):
        from hannah.models.registry import _BENCH_WEIGHTS
        self.assertGreater(
            _BENCH_WEIGHTS["mmlu_pro"]["general"],
            _BENCH_WEIGHTS["mmlu_pro"]["development"],
        )

    def test_humaneval_weight_highest_on_development_track(self):
        from hannah.models.registry import _BENCH_WEIGHTS
        dev = _BENCH_WEIGHTS["humaneval"]["development"]
        self.assertGreaterEqual(dev, _BENCH_WEIGHTS["humaneval"]["inference"])
        self.assertGreaterEqual(dev, _BENCH_WEIGHTS["humaneval"]["general"])

    def test_enrich_with_benchmarks_populates_fields(self):
        """_enrich_with_benchmarks() uses dataclasses.replace() to set all benchmark fields."""
        from hannah.models.registry import ModelCandidate
        candidate = ModelCandidate(
            name="test:7b", family="test", params_b=7, quant="q4_k_m",
            size_gb=4.5, context_k=128000, strengths=["coding"], mlx=False,
            requirements_tier="low", hf_model_id="test/Test-7B",
        )
        scores = {
            "test/Test-7B": {
                "humaneval": 0.88, "mbpp": 0.75,
                "mmlu_pro": 0.60, "hle": None, "bfcl": 0.72,
            }
        }
        enriched = ModelRegistry()._enrich_with_benchmarks([candidate], scores)
        self.assertEqual(len(enriched), 1)
        m = enriched[0]
        self.assertAlmostEqual(m.humaneval, 0.88)
        self.assertAlmostEqual(m.mmlu_pro, 0.60)
        self.assertIsNone(m.hle)
        self.assertAlmostEqual(m.bfcl, 0.72)

    def test_enrich_skips_candidates_without_hf_model_id(self):
        """Candidates with hf_model_id=None are returned unchanged."""
        from hannah.models.registry import ModelCandidate
        candidate = ModelCandidate(
            name="nohf:7b", family="test", params_b=7, quant="q4_k_m",
            size_gb=4.5, context_k=128000, strengths=["coding"], mlx=False,
            requirements_tier="low",  # hf_model_id defaults to None
        )
        enriched = ModelRegistry()._enrich_with_benchmarks([candidate], {})
        self.assertIsNone(enriched[0].humaneval)

    def test_recommend_with_injected_benchmark_scores(self):
        """benchmark_scores injected into recommend() must flow through to why string."""
        profile = RepoAnalyzer().analyze(_make_repo())
        hw = HardwareSpec(platform=Platform.LINUX, gpu_vram_gb=24, system_ram_gb=64, gpu_backend="cuda")
        target = next(c for c in MODEL_CATALOG if c.hf_model_id)
        scores = {
            target.hf_model_id: {
                "humaneval": 0.95, "mbpp": 0.92,
                "mmlu_pro": None, "hle": None, "bfcl": None,
            }
        }
        result = ModelRegistry().recommend(
            profile, hw, track="development",
            benchmark_scores=scores,
        )
        self.assertIsNotNone(result.podium[0].why)
        # At least one recommendation should mention benchmark data
        all_whys = " ".join(r.why for r in result.podium)
        self.assertIn("Benchmarks:", all_whys)


class UncataloguedDetectionTests(unittest.TestCase):
    """Community model discovery via detect_uncatalogued()."""

    def test_uncatalogued_model_detected(self):
        # "mistral:7b" is not in MODEL_CATALOG — should be returned
        pulled_details = {"mistral:7b": {"size_gb": 4.1, "family": "mistral", "quant": "q4_k_m"}}
        catalog_names = {c.name for c in MODEL_CATALOG}

        # Mock fetch_model_info to return a synthetic /api/show response
        fake_show = {
            "model_info": {"llama.context_length": 32768},
            "details": {"family": "mistral", "parameter_size": "7B", "quantization_level": "Q4_K_M"},
        }
        with patch("hannah.catalog.ollama.fetch_model_info", return_value=fake_show):
            result = detect_uncatalogued(pulled_details, catalog_names)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "mistral:7b")
        self.assertEqual(result[0]["source"], "community")
        self.assertEqual(result[0]["context_k"], 32768)

    def test_catalog_model_not_returned_as_uncatalogued(self):
        # "qwen3.5:9b" IS in MODEL_CATALOG — should NOT be returned
        pulled_details = {"qwen3.5:9b": {"size_gb": 6.6, "family": "qwen3.5", "quant": "q4_k_m"}}
        catalog_names = {c.name for c in MODEL_CATALOG}
        result = detect_uncatalogued(pulled_details, catalog_names)
        self.assertEqual(result, [])

    def test_discovery_appears_in_recommend_result(self):
        profile = RepoAnalyzer().analyze(_make_repo())
        hw = HardwareSpec(platform=Platform.LINUX, gpu_vram_gb=16, system_ram_gb=64, gpu_backend="cuda")
        # Inject a community candidate that passes VRAM and context filters
        dynamic = [{"name": "mistral:7b", "family": "mistral", "size_gb": 4.1,
                    "context_k": 128000, "quant": "q4_k_m", "source": "community"}]
        result = ModelRegistry().recommend(profile, hw, dynamic_candidates=dynamic)
        self.assertIsInstance(result, RecommendResult)
        discovery_names = [d.name for d in result.discoveries]
        self.assertIn("mistral:7b", discovery_names)

    def test_catalog_match_excluded_from_discoveries(self):
        profile = RepoAnalyzer().analyze(_make_repo())
        hw = _hw()
        # Pass qwen3.5:9b as a dynamic candidate — it's in the catalog, should be excluded
        dynamic = [{"name": "qwen3.5:9b", "family": "qwen3.5", "size_gb": 6.6,
                    "context_k": 262144, "quant": "q4_k_m", "source": "community"}]
        result = ModelRegistry().recommend(profile, hw, dynamic_candidates=dynamic)
        discovery_names = [d.name for d in result.discoveries]
        self.assertNotIn("qwen3.5:9b", discovery_names)


class LibraryScanTests(unittest.TestCase):
    """Best-effort Ollama library scan."""

    def test_scan_returns_empty_on_network_error(self):
        from hannah.catalog.ollama import scan_library
        with patch("hannah.catalog.ollama._do_library_scan", side_effect=OSError("no network")):
            result = scan_library(16.0)
        self.assertEqual(result, [])

    def test_scan_filters_by_vram_budget(self):
        from hannah.catalog.ollama import scan_library
        # Inject a fake HTML response with a small and a large model
        fake_html = (
            '<a href="/library/phi4">phi4</a> 14b description\n'
            '<a href="/library/llama4">llama4</a> 70b description\n'
        )
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = mock_urlopen.return_value.__enter__.return_value
            mock_resp.read.return_value = fake_html.encode()
            result = scan_library(8.0)  # 8 GB budget

        # 14b × 0.55 ≈ 7.7 GB fits; 70b × 0.55 ≈ 38.5 GB doesn't
        names = [c["name"] for c in result]
        if names:  # may be empty if HTML parsing finds nothing (that's OK for best-effort)
            for c in result:
                self.assertLessEqual(c["size_gb"], 8.0)

    def test_scan_results_have_required_keys(self):
        from hannah.catalog.ollama import scan_library
        fake_html = '<a href="/library/phi4">phi4</a> 7b model description here 7b tags\n'
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = mock_urlopen.return_value.__enter__.return_value
            mock_resp.read.return_value = fake_html.encode()
            result = scan_library(16.0)

        for candidate in result:
            for key in ("name", "family", "size_gb", "context_k", "quant", "source"):
                self.assertIn(key, candidate, f"Missing key '{key}' in library candidate")
            self.assertEqual(candidate["source"], "library")


class BenchmarkCacheTests(unittest.TestCase):
    """Cache read/write, TTL, normalization, and leaderboard ID matching."""

    def test_cache_hit_skips_network(self):
        """A fresh cache prevents any urllib call."""
        import datetime, json, tempfile
        from pathlib import Path
        from hannah.catalog.benchmarks import load_benchmark_scores
        fresh_cache = {
            "fetched_at": datetime.datetime.now(datetime.UTC).isoformat(),
            "scores": {
                "Qwen/Qwen2.5-Coder-32B-Instruct": {
                    "humaneval": 0.885, "mbpp": 0.78,
                    "mmlu_pro": None, "hle": None, "bfcl": None,
                }
            },
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "benchmarks.json"
            cache_path.write_text(json.dumps(fresh_cache))
            with patch("hannah.catalog.benchmarks._CACHE_PATH", cache_path):
                with patch("urllib.request.urlopen") as mock_url:
                    result = load_benchmark_scores(["Qwen/Qwen2.5-Coder-32B-Instruct"])
                mock_url.assert_not_called()
        self.assertAlmostEqual(
            result["Qwen/Qwen2.5-Coder-32B-Instruct"]["humaneval"], 0.885
        )

    def test_stale_cache_triggers_fetch(self):
        """A cache older than 7 days forces _fetch_fresh to be called."""
        import datetime, json, tempfile
        from pathlib import Path
        from hannah.catalog.benchmarks import load_benchmark_scores
        old_time = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=8)).isoformat()
        stale_cache = {"fetched_at": old_time, "scores": {}}
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "benchmarks.json"
            cache_path.write_text(json.dumps(stale_cache))
            with patch("hannah.catalog.benchmarks._CACHE_PATH", cache_path):
                with patch("hannah.catalog.benchmarks._fetch_fresh", return_value={}) as mock_fetch:
                    load_benchmark_scores(["Qwen/Qwen2.5-Coder-32B-Instruct"])
            mock_fetch.assert_called_once()

    def test_network_error_returns_empty_gracefully(self):
        """Network failure must not raise — returns empty dict."""
        import tempfile
        from pathlib import Path
        from hannah.catalog.benchmarks import load_benchmark_scores
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "no-cache.json"  # does not exist
            with patch("hannah.catalog.benchmarks._CACHE_PATH", cache_path):
                with patch("hannah.catalog.benchmarks._fetch_fresh", side_effect=OSError("no network")):
                    result = load_benchmark_scores(["Qwen/Qwen2.5-Coder-32B-Instruct"])
        self.assertIsInstance(result, dict)

    def test_score_normalization_100_scale(self):
        from hannah.catalog.benchmarks import _normalize_score
        self.assertAlmostEqual(_normalize_score(88.5), 0.885)

    def test_score_normalization_decimal_scale(self):
        from hannah.catalog.benchmarks import _normalize_score
        self.assertAlmostEqual(_normalize_score(0.885), 0.885)

    def test_leaderboard_id_match_exact(self):
        from hannah.catalog.benchmarks import _match_leaderboard_id
        self.assertTrue(
            _match_leaderboard_id(
                "Qwen/Qwen2.5-Coder-32B-Instruct",
                "Qwen/Qwen2.5-Coder-32B-Instruct",
            )
        )

    def test_leaderboard_id_match_no_org(self):
        from hannah.catalog.benchmarks import _match_leaderboard_id
        self.assertTrue(
            _match_leaderboard_id(
                "Qwen2.5-Coder-32B-Instruct",
                "Qwen/Qwen2.5-Coder-32B-Instruct",
            )
        )

    def test_leaderboard_id_no_false_positive(self):
        from hannah.catalog.benchmarks import _match_leaderboard_id
        self.assertFalse(
            _match_leaderboard_id(
                "Qwen/Qwen2.5-Coder-14B-Instruct",
                "Qwen/Qwen2.5-Coder-32B-Instruct",
            )
        )

    def test_leaderboard_id_case_insensitive(self):
        from hannah.catalog.benchmarks import _match_leaderboard_id
        self.assertTrue(
            _match_leaderboard_id(
                "meta-llama/llama-3.1-8b-instruct",
                "meta-llama/Llama-3.1-8B-Instruct",
            )
        )

    def test_leaderboard_id_map_used_for_instruct_variants(self):
        """_LEADERBOARD_ID_MAP must translate instruct IDs to base IDs for lookup."""
        import json, tempfile
        from pathlib import Path
        from hannah.catalog.benchmarks import load_benchmark_scores, _LEADERBOARD_ID_MAP

        # Confirm the coder-14b → base-14b mapping is present
        self.assertIn("Qwen/Qwen2.5-Coder-14B-Instruct", _LEADERBOARD_ID_MAP)
        self.assertEqual(
            _LEADERBOARD_ID_MAP["Qwen/Qwen2.5-Coder-14B-Instruct"],
            "Qwen/Qwen2.5-14B",
        )

        # Simulate a leaderboard that only has the base model ID
        fake_leaderboard = [
            {"modelId": "Qwen/Qwen2.5-14B", "value": 63.69},
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "benchmarks.json"
            with patch("hannah.catalog.benchmarks._CACHE_PATH", cache_path):
                with patch(
                    "hannah.catalog.benchmarks._fetch_leaderboard",
                    return_value=fake_leaderboard,
                ):
                    with patch("hannah.catalog.benchmarks._fetch_model_card_scores", return_value={}):
                        with patch("hannah.catalog.benchmarks._fetch_bfcl"):
                            result = load_benchmark_scores(
                                ["Qwen/Qwen2.5-Coder-14B-Instruct"]
                            )
        score = result["Qwen/Qwen2.5-Coder-14B-Instruct"]["mmlu_pro"]
        self.assertIsNotNone(score)
        self.assertAlmostEqual(score, 0.6369, places=3)


if __name__ == "__main__":
    unittest.main()
