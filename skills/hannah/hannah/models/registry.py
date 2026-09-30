"""Model registry and recommendation engine."""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any, Optional

from ..hardware.detect import HardwareSpec, Platform
from ..catalog.ollama import names_match


@dataclass(frozen=True)
class ModelCandidate:
    name: str
    family: str
    params_b: float
    quant: str
    size_gb: float
    context_k: int
    strengths: list[str]
    mlx: bool
    requirements_tier: str
    pulled: bool = False
    humaneval: Optional[float] = None    # HumanEval pass@1, 0.0–1.0
    mbpp: Optional[float] = None         # MBPP pass@1, 0.0–1.0
    hf_model_id: Optional[str] = None   # HuggingFace repo ID for benchmark lookup
    mmlu_pro: Optional[float] = None     # MMLU-Pro score, 0.0–1.0
    hle: Optional[float] = None          # HLE score, 0.0–1.0
    bfcl: Optional[float] = None         # BFCL score, 0.0–1.0


@dataclass(frozen=True)
class Recommendation:
    model: ModelCandidate
    rank: int
    why: str
    tag: str


@dataclass(frozen=True)
class Discovery:
    """An unscored model candidate surfaced via dynamic discovery."""
    name: str
    family: str
    size_gb: float
    context_k: int
    quant: str
    source: str   # "community" (locally installed) | "library" (Ollama registry)
    pulled: bool = False  # True for community (already installed locally)

    @property
    def tag(self) -> str:
        return f"{self.source} · unscored"


@dataclass
class RecommendResult:
    """Return type of ModelRegistry.recommend().

    Behaves like a list of Recommendation for backward-compatible iteration
    (iterates over podium). Access .discoveries for unscored dynamic candidates.
    """
    podium: list[Recommendation]
    discoveries: list[Discovery] = field(default_factory=list)

    def __iter__(self):
        return iter(self.podium)

    def __len__(self):
        return len(self.podium)

    def __bool__(self):
        return bool(self.podium)

    def __getitem__(self, idx):
        return self.podium[idx]


# Per-eval per-track scoring weights.
# Higher weight = this benchmark matters more on that track.
_BENCH_WEIGHTS: dict[str, dict[str, float]] = {
    "humaneval": {"development": 1.5, "inference": 0.5, "general": 0.7},
    "mbpp":      {"development": 1.2, "inference": 0.4, "general": 0.6},
    "mmlu_pro":  {"development": 0.5, "inference": 0.8, "general": 1.0},
    "hle":       {"development": 0.3, "inference": 0.6, "general": 0.8},
    "bfcl":      {"development": 0.8, "inference": 0.3, "general": 0.6},
}


MODEL_CATALOG: list[ModelCandidate] = [
    ModelCandidate(
        name="qwen3.5:9b-mlx",
        family="qwen3.5",
        params_b=9,
        quant="mlx",
        size_gb=8.9,
        context_k=262144,
        strengths=["general", "coding", "multilingual", "fast_metal"],
        mlx=True,
        requirements_tier="low",
        hf_model_id="Qwen/Qwen3.5-9B-Instruct",
    ),
    ModelCandidate(
        name="qwen3.5:9b",
        family="qwen3.5",
        params_b=9,
        quant="q4_k_m",
        size_gb=6.6,
        context_k=262144,
        strengths=["general", "coding", "multilingual", "vision"],
        mlx=False,
        requirements_tier="low",
        hf_model_id="Qwen/Qwen3.5-9B-Instruct",
    ),
    ModelCandidate(
        name="gemma4:12b-mlx",
        family="gemma4",
        params_b=12,
        quant="mlx",
        size_gb=10.0,
        context_k=131072,
        strengths=["reasoning", "agentic", "coding", "fast_metal"],
        mlx=True,
        requirements_tier="mid",
        hf_model_id="google/gemma-4-12b-it",
    ),
    ModelCandidate(
        name="gemma4:12b",
        family="gemma4",
        params_b=12,
        quant="q4_k_m",
        size_gb=7.6,
        context_k=131072,
        strengths=["reasoning", "agentic", "coding", "vision"],
        mlx=False,
        requirements_tier="low",
        hf_model_id="google/gemma-4-12b-it",
    ),
    ModelCandidate(
        name="qwen2.5-coder:14b-instruct-q4_k_m",
        family="qwen2.5-coder",
        params_b=14,
        quant="q4_k_m",
        size_gb=8.2,
        context_k=32768,
        strengths=["coding", "refactor", "tests", "debugging"],
        mlx=False,
        requirements_tier="low",
        hf_model_id="Qwen/Qwen2.5-Coder-14B-Instruct",
    ),
    ModelCandidate(
        name="qwen2.5-coder:32b-instruct-q5_k_m",
        family="qwen2.5-coder",
        params_b=32,
        quant="q5_k_m",
        size_gb=15.5,
        context_k=32768,
        strengths=["coding", "architecture", "large_repos"],
        mlx=False,
        requirements_tier="mid",
        hf_model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
    ),
    ModelCandidate(
        name="qwen2.5-coder:72b-instruct-q4_k_m",
        family="qwen2.5-coder",
        params_b=72,
        quant="q4_k_m",
        size_gb=38.5,
        context_k=32768,
        strengths=["coding", "deep_review", "best_quality"],
        mlx=False,
        requirements_tier="high",
        hf_model_id="Qwen/Qwen2.5-Coder-72B-Instruct",
    ),
    ModelCandidate(
        name="qwen3:14b-q4_k_m",
        family="qwen3",
        params_b=14,
        quant="q4_k_m",
        size_gb=9.0,
        context_k=40960,
        strengths=["reasoning", "tool_use", "general"],
        mlx=False,
        requirements_tier="low",
        hf_model_id="Qwen/Qwen3-14B",
    ),
    ModelCandidate(
        name="llama3.1:8b-q6_k",
        family="llama3.1",
        params_b=8,
        quant="q6_k",
        size_gb=6.8,
        context_k=128000,
        strengths=["general", "chat", "fast"],
        mlx=False,
        requirements_tier="low",
        hf_model_id="meta-llama/Llama-3.1-8B-Instruct",
    ),
]


@dataclass
class ModelRegistry:
    def recommend(
        self,
        repo_profile: Any,
        hardware: Any,
        track: str = "development",
        pulled_models: Optional[set[str]] = None,
        dynamic_candidates: Optional[list[dict]] = None,
        benchmark_scores: Optional[dict[str, dict[str, Optional[float]]]] = None,
    ) -> RecommendResult:
        candidates = self._enrich_with_pull_status(MODEL_CATALOG, pulled_models or set())
        if benchmark_scores:
            candidates = self._enrich_with_benchmarks(candidates, benchmark_scores)
        eligible = self._filter_by_hardware(candidates, hardware, track)
        scored = self._score(eligible, repo_profile, hardware, track)
        podium = [
            Recommendation(model=c, rank=i + 1, why=s["why"], tag=s["tag"])
            for i, (c, s) in enumerate(scored[:5])
        ]

        catalog_names = {c.name for c in MODEL_CATALOG}
        discoveries = self._filter_discoveries(
            dynamic_candidates or [], catalog_names, hardware, track
        )

        return RecommendResult(podium=podium, discoveries=discoveries)

    def _enrich_with_pull_status(
        self,
        candidates: list[ModelCandidate],
        pulled_models: set[str],
    ) -> list[ModelCandidate]:
        if not pulled_models:
            return candidates
        enriched = []
        for c in candidates:
            is_pulled = any(names_match(ollama_name, c.name) for ollama_name in pulled_models)
            enriched.append(dataclasses.replace(c, pulled=is_pulled) if is_pulled else c)
        return enriched

    def _enrich_with_benchmarks(
        self,
        candidates: list[ModelCandidate],
        scores: dict[str, dict[str, Optional[float]]],
    ) -> list[ModelCandidate]:
        enriched = []
        for c in candidates:
            if c.hf_model_id and c.hf_model_id in scores:
                s = scores[c.hf_model_id]
                enriched.append(dataclasses.replace(
                    c,
                    humaneval=s.get("humaneval"),
                    mbpp=s.get("mbpp"),
                    mmlu_pro=s.get("mmlu_pro"),
                    hle=s.get("hle"),
                    bfcl=s.get("bfcl"),
                ))
            else:
                enriched.append(c)
        return enriched

    def _filter_by_hardware(
        self, candidates: list[ModelCandidate], hardware: Any, track: str = "development"
    ) -> list[ModelCandidate]:
        out: list[ModelCandidate] = []
        plat = getattr(hardware, "platform", "unknown")
        min_ctx = 64000 if track in ("development", "general") else 0
        for c in candidates:
            if c.mlx and plat != "darwin":
                continue
            if c.context_k < min_ctx:
                continue
            vram = getattr(hardware, "gpu_vram_gb", 0) or 0
            ram = getattr(hardware, "system_ram_gb", 0) or 0
            if plat == "darwin" and c.mlx:
                out.append(c)
            elif c.size_gb <= vram * 1.0:
                out.append(c)
            elif c.size_gb <= vram * 1.25:
                out.append(c)
            elif ram >= 32 and c.requirements_tier != "high":
                out.append(c)
        return out if out else candidates[:3]

    def _filter_discoveries(
        self,
        dynamic_candidates: list[dict],
        catalog_names: set[str],
        hardware: Any,
        track: str,
    ) -> list[Discovery]:
        """Filter dynamic candidates by VRAM fit and context window.

        Community candidates (locally installed) are checked against the context
        filter because we have accurate GGUF data for them. Library candidates
        have unknown context (0) and skip the context check.
        """
        vram = getattr(hardware, "gpu_vram_gb", 0) or 0
        ram = getattr(hardware, "system_ram_gb", 0) or 0
        plat = getattr(hardware, "platform", "unknown")
        min_ctx = 64000 if track in ("development", "general") else 0

        community: list[Discovery] = []
        library: list[Discovery] = []

        for c in dynamic_candidates:
            name = c.get("name", "")
            size_gb = c.get("size_gb") or 0.0
            context_k = c.get("context_k") or 0
            source = c.get("source", "community")

            if any(names_match(name, cn) for cn in catalog_names):
                continue

            if source == "community" and context_k > 0 and context_k < min_ctx:
                continue

            if size_gb == 0:
                fits = True
            elif plat == "darwin":
                fits = True
            elif size_gb <= vram * 1.25:
                fits = True
            elif ram >= 32:
                fits = True
            else:
                fits = False

            if not fits:
                continue

            d = Discovery(
                name=name,
                family=c.get("family", ""),
                size_gb=size_gb,
                context_k=context_k,
                quant=c.get("quant", "unknown"),
                source=source,
                pulled=(source == "community"),
            )
            if source == "community":
                community.append(d)
            else:
                library.append(d)

        community.sort(key=lambda d: d.size_gb)
        library.sort(key=lambda d: d.size_gb)
        combined = community[:3] + library[:3]
        return combined[:5]

    def _score(
        self,
        candidates: list[ModelCandidate],
        repo: Any,
        hardware: Any,
        track: str,
    ) -> list[tuple[ModelCandidate, dict]]:
        vram = getattr(hardware, "gpu_vram_gb", 0) or 0
        scored: list[tuple[ModelCandidate, dict]] = []
        track_map = {
            "development": {"coding", "refactor", "tests", "debugging", "fast", "general", "reasoning", "fast_metal"},
            "inference": {"general", "chat", "fast", "fast_metal", "multilingual"},
            "general": {"coding", "general", "reasoning", "multilingual", "agentic"},
        }
        targets = track_map.get(track, set())
        for c in candidates:
            score = 0.0
            s: dict = {"why": "", "tag": "", "penalties": []}
            plat = getattr(hardware, "platform", "unknown")

            # VRAM / platform fit
            if plat == "darwin" and c.mlx:
                score += 3
                s["tag"] = "MLX optimized"
            elif c.size_gb <= (vram or 999) * 0.85:
                score += 3
                s["tag"] = "Fits in VRAM"
            elif c.size_gb <= (vram or 999) * 1.25:
                score += 1.5
                s["tag"] = "Partial offload"
                s["penalties"].append("partial offload")

            # Model size bracket
            if c.size_gb < 8:
                score += 1
            elif c.size_gb < 14:
                score += 2
            elif c.size_gb < 22:
                score += 1.5
            else:
                score -= 1
                s["penalties"].append("heavy model")

            # Track alignment
            overlap = len(set(c.strengths) & targets)
            score += min(3.0, overlap * 0.7)

            # Context window
            if c.context_k >= 256000:
                score += 1
            elif c.context_k >= 128000:
                score += 0.7
            elif c.context_k >= 64000:
                score += 0.4

            # Complexity match
            if repo.complexity_score < 4 and c.requirements_tier == "low":
                score += 1
            elif repo.complexity_score >= 7 and c.requirements_tier == "high":
                score += 1.5
            elif repo.complexity_score >= 5 and c.requirements_tier == "mid":
                score += 1

            # Multi-benchmark signal with per-eval per-track weights
            bench_fields = {
                "humaneval": c.humaneval, "mbpp": c.mbpp,
                "mmlu_pro":  c.mmlu_pro,  "hle":  c.hle,  "bfcl": c.bfcl,
            }
            bench_bonus = 0.0
            bench_labels = []
            for eval_name, val in bench_fields.items():
                if val is None:
                    continue
                w = _BENCH_WEIGHTS.get(eval_name, {}).get(track, 0.0)
                if w == 0.0:
                    continue
                if val >= 0.90:
                    tier_bonus = 1.5
                elif val >= 0.80:
                    tier_bonus = 1.0
                elif val >= 0.70:
                    tier_bonus = 0.5
                else:
                    tier_bonus = 0.0
                bench_bonus += tier_bonus * w
                if tier_bonus > 0:
                    bench_labels.append(f"{eval_name}={val:.0%}")
            score += bench_bonus

            # Pull status — tie-breaker only (+0.5)
            if c.pulled:
                score += 0.5
                pull_label = "ready to race"
            else:
                pull_label = "pull required"

            if s["tag"]:
                s["tag"] = f"{s['tag']} · {pull_label}"
            else:
                s["tag"] = pull_label

            penalties_str = ", ".join(s["penalties"]) if s["penalties"] else "clean fit"
            s["score"] = round(score, 2)
            s["why"] = (
                f"{c.size_gb:.1f} GB/{c.quant}, {c.context_k // 1000}K ctx. "
                f"Strengths: {', '.join(c.strengths[:3])}. "
                f"Fit: {penalties_str}."
            )
            if bench_labels:
                s["why"] += f" Benchmarks: {', '.join(bench_labels[:3])}."
            scored.append((c, s))

        scored.sort(key=lambda x: (-x[1]["score"], x[0].size_gb, not x[0].pulled))
        return scored
