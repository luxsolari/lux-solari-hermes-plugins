"""Ollama catalog probe — detect locally pulled models and discover new candidates.

Pure stdlib. Three probe strategies in this module:
  1. Local REST API (/api/tags)  — primary source for pulled models
  2. Local REST API (/api/show)  — GGUF metadata per model (context window, etc.)
  3. Ollama library scrape        — best-effort; fails silently on network error

Any failure at any level silently returns an empty result so the rest of Hannah
is unaffected when Ollama isn't installed or isn't running.
"""

from __future__ import annotations

import json
import re
import subprocess
import urllib.request
from typing import Optional

_OLLAMA_TAGS = "http://localhost:11434/api/tags"
_OLLAMA_SHOW = "http://localhost:11434/api/show"
_LIBRARY_URL = "https://ollama.com/library"
_TIMEOUT = 2        # seconds — localhost only; 2s is generous
_SHOW_TIMEOUT = 3   # /api/show may take slightly longer
_LIBRARY_TIMEOUT = 5


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def is_ollama_available() -> bool:
    """Return True if the `ollama` binary is on PATH."""
    try:
        subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            timeout=_TIMEOUT,
        )
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


def get_pulled_model_details() -> dict[str, dict]:
    """Return {name: {size_gb, family, quant}} for all locally pulled models.

    Tries the REST API first (richer data), falls back to CLI (names only).
    Always returns a dict — empty if Ollama is unavailable.
    """
    details = _probe_rest_api_detailed()
    if details is not None:
        return details
    names = _probe_cli()
    if names:
        return {n: {"size_gb": None, "family": "", "quant": ""} for n in names}
    return {}


def detect_pulled_models() -> set[str]:
    """Return the set of model names currently pulled in the local Ollama instance.

    Convenience wrapper around get_pulled_model_details(). Always returns a set.
    """
    return set(get_pulled_model_details().keys())


def fetch_model_info(name: str) -> Optional[dict]:
    """POST /api/show for a single model. Returns the full JSON dict or None on error."""
    try:
        payload = json.dumps({"name": name, "verbose": False}).encode()
        req = urllib.request.Request(
            _OLLAMA_SHOW,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=_SHOW_TIMEOUT) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def extract_gguf_context(show_response: dict) -> Optional[int]:
    """Find the first *.context_length key in model_info and return its integer value."""
    for k, v in show_response.get("model_info", {}).items():
        if k.endswith(".context_length"):
            try:
                return int(v)
            except (TypeError, ValueError):
                pass
    return None


def detect_uncatalogued(pulled_details: dict[str, dict], catalog_names: set[str]) -> list[dict]:
    """Find locally pulled models not covered by the static catalog.

    Calls /api/show for each uncatalogued model (up to 5) to get GGUF context window.
    Returns a list of candidate dicts with source='community'.
    """
    uncatalogued = [
        name for name in pulled_details
        if not any(names_match(name, cn) for cn in catalog_names)
    ]

    result: list[dict] = []
    for name in uncatalogued[:5]:
        info = pulled_details[name]
        show = fetch_model_info(name)
        context_k = extract_gguf_context(show) if show else 0
        result.append({
            "name": name,
            "family": info.get("family") or "",
            "size_gb": info.get("size_gb") or 0.0,
            "context_k": context_k or 0,
            "quant": info.get("quant") or "unknown",
            "source": "community",
        })

    return result


def scan_library(vram_budget_gb: float) -> list[dict]:
    """Best-effort scrape of https://ollama.com/library for models fitting the VRAM budget.

    Returns up to 5 candidate dicts with source='library'.
    Fails completely silently — returns [] on any network or parsing error.
    """
    try:
        return _do_library_scan(vram_budget_gb)
    except Exception:
        return []


def names_match(ollama_name: str, catalog_name: str) -> bool:
    """Return True if an Ollama model name corresponds to a catalog entry.

    Ollama reports quant suffixes in mixed case (e.g. q4_K_M) while the
    catalog stores them lowercase (q4_k_m). Both sides are lowercased and
    their quant suffixes stripped before comparison so the following all match:

      "qwen2.5-coder:14b-instruct-q4_K_M"  ↔  "qwen2.5-coder:14b-instruct-q4_k_m"
      "qwen3:14b"                           ↔  "qwen3:14b-q4_k_m"

    Note: :latest tags are NOT treated as aliases for specific versions.
    "gemma4:latest" does not match "gemma4:12b" because :latest is volatile
    and may point to a different model variant over time.
    """
    if ollama_name.lower() == catalog_name.lower():
        return True
    return _strip_quant(ollama_name).lower() == _strip_quant(catalog_name).lower()


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _probe_rest_api_detailed() -> Optional[dict[str, dict]]:
    """Query /api/tags and return {name: {size_gb, family, quant}} per model."""
    try:
        with urllib.request.urlopen(_OLLAMA_TAGS, timeout=_TIMEOUT) as resp:
            data = json.loads(resp.read())
        result: dict[str, dict] = {}
        for m in data.get("models", []):
            name = m.get("name", "")
            if not name:
                continue
            details = m.get("details", {})
            result[name] = {
                "size_gb": round(m.get("size", 0) / 1e9, 1),
                "family": details.get("family", ""),
                "quant": details.get("quantization_level", "").lower(),
            }
        return result
    except Exception:
        return None


def _probe_cli() -> Optional[set[str]]:
    """Parse `ollama list` table output. Returns None on any failure."""
    try:
        out = subprocess.check_output(
            ["ollama", "list"],
            text=True,
            timeout=_TIMEOUT,
            stderr=subprocess.DEVNULL,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError, OSError):
        return None

    names: set[str] = set()
    for line in out.splitlines()[1:]:  # skip header row
        parts = line.split()
        if parts:
            names.add(parts[0])
    return names or None


def _do_library_scan(vram_budget_gb: float) -> list[dict]:
    """Inner implementation of scan_library(); may raise — caller wraps in try/except."""
    req = urllib.request.Request(
        _LIBRARY_URL,
        headers={"User-Agent": "hannah/0.7 (best-effort library scan)"},
    )
    with urllib.request.urlopen(req, timeout=_LIBRARY_TIMEOUT) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    candidates: list[dict] = []
    seen_names: set[str] = set()

    # Extract model family slugs from library hrefs
    families = list(dict.fromkeys(
        re.findall(r'href=["\']\/library\/([a-z][a-z0-9._-]*)["\']', html)
    ))

    for family in families[:60]:
        # Find all parameter size hints in a window around the family's first mention
        idx = html.find(f"/library/{family}")
        if idx < 0:
            continue
        window = html[max(0, idx - 100):idx + 600]

        # Match standalone number followed by 'b' (e.g. "9b", "14b", "72b")
        param_matches = re.findall(r'\b(\d+(?:\.\d+)?)\s*[bB]\b', window)
        if not param_matches:
            continue

        for p_str in param_matches[:4]:
            try:
                params_b = float(p_str)
            except ValueError:
                continue
            if params_b < 1 or params_b > 200:
                continue

            # Rough q4 size estimate: params_b × 0.55 GB
            est_gb = round(params_b * 0.55, 1)
            if est_gb > vram_budget_gb:
                continue

            name = f"{family}:{int(params_b)}b"
            if name in seen_names:
                continue
            seen_names.add(name)

            candidates.append({
                "name": name,
                "family": family,
                "size_gb": est_gb,
                "context_k": 0,
                "quant": "q4_k_m",  # estimated
                "source": "library",
            })

    candidates.sort(key=lambda c: c["size_gb"])
    return candidates[:5]


def _parse_params(param_str: str) -> float:
    """Parse a parameter size string to float billions. '9.4B' → 9.4, '14B' → 14.0."""
    if not param_str:
        return 0.0
    s = param_str.strip().upper().rstrip("B").strip()
    try:
        return float(s)
    except ValueError:
        return 0.0


def _strip_quant(name: str) -> str:
    """Remove a trailing quant suffix from a model name.

    "qwen2.5-coder:14b-q4_k_m" → "qwen2.5-coder:14b"
    "gemma4:12b-mlx"            → "gemma4:12b"
    "llama3.1:8b-q6_k"         → "llama3.1:8b"
    "qwen3.5:9b"                → "qwen3.5:9b"  (no quant suffix)
    """
    _QUANT_PREFIXES = ("q2_", "q3_", "q4_", "q5_", "q6_", "q8_", "mlx", "fp16", "bf16")
    if ":" not in name:
        return name
    base, tag = name.rsplit(":", 1)
    if "-" in tag:
        param, quant = tag.rsplit("-", 1)
        if any(quant.lower().startswith(p) for p in _QUANT_PREFIXES):
            return f"{base}:{param}"
    return name
