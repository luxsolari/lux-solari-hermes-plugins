"""Live benchmark score fetching with 7-day file cache.

Fetches scores from:
- HuggingFace model card eval_results (HumanEval, MBPP)
- HuggingFace dataset leaderboards (MMLU-Pro, HLE)
- BFCL leaderboard best-effort (gorilla.cs.berkeley.edu)

All network calls are wrapped in try/except — any failure returns no scores
for that source. The caller always gets a dict (possibly empty) and never
sees an exception.
"""

from __future__ import annotations

import datetime
import json
import urllib.request
from pathlib import Path
from typing import Optional

_CACHE_PATH = Path.home() / ".cache" / "hannah" / "benchmarks.json"
_CACHE_TTL_DAYS = 7
_HF_API_TIMEOUT = 8
_HF_MODEL_URL = "https://huggingface.co/api/models/{hf_model_id}"
_HF_LEADERBOARD_URL = "https://huggingface.co/api/datasets/{dataset_id}/leaderboard"
_BFCL_URL = "https://gorilla.cs.berkeley.edu/leaderboard_data.json"
_MMLU_PRO_DATASET = "TIGER-Lab/MMLU-Pro"
_HLE_DATASET = "cais/hle"

_EMPTY_SCORES: dict[str, Optional[float]] = {
    "humaneval": None, "mbpp": None,
    "mmlu_pro": None, "hle": None, "bfcl": None,
}

_CODING_DATASETS = {
    "openai/humaneval": "humaneval",
    "humaneval": "humaneval",
    "google-research-datasets/mbpp": "mbpp",
    "mbpp": "mbpp",
}

# Leaderboards index base/non-instruct model IDs; our hf_model_id values
# are instruct/coder variants. Map instruct → base for leaderboard lookups.
_LEADERBOARD_ID_MAP: dict[str, str] = {
    "Qwen/Qwen2.5-Coder-14B-Instruct": "Qwen/Qwen2.5-14B",
    "Qwen/Qwen2.5-Coder-32B-Instruct": "Qwen/Qwen2.5-32B",
    "Qwen/Qwen2.5-Coder-72B-Instruct": "Qwen/Qwen2.5-72B",
    "meta-llama/Llama-3.1-8B-Instruct": "meta-llama/Llama-3.1-8B",
}


def load_benchmark_scores(
    hf_model_ids: list[str],
    *,
    force_refresh: bool = False,
) -> dict[str, dict[str, Optional[float]]]:
    """Return {hf_model_id: {eval: score}} for the given model IDs.

    Reads from cache if fresh (< 7 days) and all requested IDs are present.
    Fetches live sources otherwise. Never raises.
    """
    if not hf_model_ids:
        return {}

    if not force_refresh:
        cached = _load_cache()
        if cached is not None:
            scores = cached.get("scores", {})
            if all(mid in scores for mid in hf_model_ids):
                return {mid: scores[mid] for mid in hf_model_ids}

    try:
        fresh = _fetch_fresh(hf_model_ids)
    except Exception:
        fresh = {}

    # Merge fresh results with stale cache entries (keeps previously fetched models)
    try:
        old = _load_cache(ignore_ttl=True)
        merged = dict(old.get("scores", {}) if old else {})
        merged.update(fresh)
    except Exception:
        merged = fresh

    _save_cache(merged)
    return {mid: merged.get(mid, dict(_EMPTY_SCORES)) for mid in hf_model_ids}


def _load_cache(*, ignore_ttl: bool = False) -> Optional[dict]:
    try:
        data = json.loads(_CACHE_PATH.read_text())
        if ignore_ttl:
            return data
        fetched_at = datetime.datetime.fromisoformat(data["fetched_at"])
        # Ensure both sides are timezone-aware for subtraction
        if fetched_at.tzinfo is None:
            fetched_at = fetched_at.replace(tzinfo=datetime.UTC)
        age = datetime.datetime.now(datetime.UTC) - fetched_at
        if age.days < _CACHE_TTL_DAYS:
            return data
    except Exception:
        pass
    return None


def _save_cache(scores: dict) -> None:
    try:
        _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "fetched_at": datetime.datetime.now(datetime.UTC).isoformat(),
            "scores": scores,
        }
        _CACHE_PATH.write_text(json.dumps(payload, indent=2))
    except Exception:
        pass


def _fetch_fresh(
    hf_model_ids: list[str],
) -> dict[str, dict[str, Optional[float]]]:
    """Fetch scores from all sources for the given HF model IDs."""
    scores: dict[str, dict[str, Optional[float]]] = {
        mid: dict(_EMPTY_SCORES) for mid in hf_model_ids
    }

    # 1. Per-model HF model card (HumanEval, MBPP)
    for mid in hf_model_ids:
        try:
            card_scores = _fetch_model_card_scores(mid)
            scores[mid].update(card_scores)
        except Exception:
            pass

    # 2. MMLU-Pro leaderboard
    try:
        mmlu_entries = _fetch_leaderboard(_MMLU_PRO_DATASET)
        for mid in hf_model_ids:
            lookup_id = _LEADERBOARD_ID_MAP.get(mid, mid)
            val = _find_in_leaderboard(mmlu_entries, lookup_id)
            if val is not None:
                scores[mid]["mmlu_pro"] = val
    except Exception:
        pass

    # 3. HLE leaderboard
    try:
        hle_entries = _fetch_leaderboard(_HLE_DATASET)
        for mid in hf_model_ids:
            lookup_id = _LEADERBOARD_ID_MAP.get(mid, mid)
            val = _find_in_leaderboard(hle_entries, lookup_id)
            if val is not None:
                scores[mid]["hle"] = val
    except Exception:
        pass

    # 4. BFCL (best-effort, structure unknown)
    try:
        _fetch_bfcl(scores)
    except Exception:
        pass

    return scores


def _fetch_model_card_scores(hf_model_id: str) -> dict[str, Optional[float]]:
    """Fetch HumanEval and MBPP from a model's HuggingFace card eval_results."""
    url = _HF_MODEL_URL.format(hf_model_id=hf_model_id)
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=_HF_API_TIMEOUT) as resp:
        data = json.loads(resp.read().decode())

    result: dict[str, Optional[float]] = {}
    card = data.get("cardData") or {}
    eval_results = card.get("eval_results") or []

    for entry in eval_results:
        dataset_type = ((entry.get("dataset") or {}).get("type") or "").lower()
        eval_key = _CODING_DATASETS.get(dataset_type)
        if not eval_key:
            continue
        metrics = entry.get("metrics") or []
        for metric in metrics:
            mtype = (metric.get("type") or "").lower()
            if "pass" in mtype or "accuracy" in mtype:
                val = metric.get("value")
                if isinstance(val, (int, float)):
                    result[eval_key] = _normalize_score(float(val))
                    break

    return result


def _fetch_leaderboard(dataset_id: str) -> list[dict]:
    """Fetch a HuggingFace dataset leaderboard entry list."""
    url = _HF_LEADERBOARD_URL.format(dataset_id=dataset_id)
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=_HF_API_TIMEOUT) as resp:
        data = json.loads(resp.read().decode())
    return data if isinstance(data, list) else []


def _find_in_leaderboard(
    entries: list[dict], hf_model_id: str
) -> Optional[float]:
    """Find the score for hf_model_id in a leaderboard entry list."""
    values = [e.get("value") for e in entries if isinstance(e.get("value"), (int, float))]
    is_100_scale = any(v > 1.0 for v in values)

    for entry in entries:
        entry_id = entry.get("modelId") or entry.get("model_id") or ""
        if _match_leaderboard_id(str(entry_id), hf_model_id):
            val = entry.get("value")
            if isinstance(val, (int, float)):
                raw = float(val)
                return round(raw / 100.0, 4) if is_100_scale else round(raw, 4)
    return None


def _fetch_bfcl(scores: dict[str, dict[str, Optional[float]]]) -> None:
    """Best-effort BFCL fetch. Modifies scores in-place."""
    req = urllib.request.Request(_BFCL_URL, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=_HF_API_TIMEOUT) as resp:
        raw = resp.read().decode()

    if raw.lstrip().startswith("<"):
        return

    data = json.loads(raw)
    entries = data if isinstance(data, list) else (
        data.get("results") or data.get("data") or []
    )
    if not isinstance(entries, list):
        return

    for mid in scores:
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            entry_id = (
                entry.get("modelId") or entry.get("model")
                or entry.get("model_id") or ""
            )
            if _match_leaderboard_id(str(entry_id), mid):
                val = (
                    entry.get("score") or entry.get("value")
                    or entry.get("overall")
                )
                if isinstance(val, (int, float)):
                    scores[mid]["bfcl"] = _normalize_score(float(val))
                    break


def _match_leaderboard_id(entry_id: str, our_id: str) -> bool:
    """Match a leaderboard modelId against our hf_model_id.

    Exact match (case-insensitive) first, then strip org prefix on both sides.
    Prevents false positives between similarly named models (14B vs 32B).
    """
    a = entry_id.lower().strip()
    b = our_id.lower().strip()
    if a == b:
        return True
    return a.split("/", 1)[-1] == b.split("/", 1)[-1]


def _normalize_score(value: float) -> float:
    """Normalize to [0.0, 1.0]. Values > 1.0 are assumed to be on a 0-100 scale."""
    if value > 1.0:
        return round(value / 100.0, 4)
    return round(value, 4)
