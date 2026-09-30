---
name: hannah
description: >-
  Recommend the best local LLM models for a given codebase and machine. Use when
  the user asks which local model to run, what fits their VRAM/RAM, which Ollama
  or MLX model suits their repo, or wants a hardware-aware model recommendation
  for a project. Analyzes repo complexity + hardware, returns ranked picks.
license: MIT
---

# Hannah — F1 Strategy Engineer for Your LLM Garage

Hannah inspects a repository, reads the host hardware, and recommends the optimal
**local** LLM models (Ollama / Apple-MLX), ranked like an F1 podium. Every call is
grounded in measured repo complexity and real VRAM/RAM limits — no guessing.

## When to use this skill

- "Which local model should I run for this project?"
- "What LLM fits in my 16GB VRAM / on my M1?"
- "Recommend an Ollama / MLX model for this repo."
- Any hardware-aware local-model selection for a codebase.

## How to run the engine

The engine is a zero-dependency, pure-stdlib Python package named `hannah`
(`python3 -m hannah`). Invoke it and read its output — do not reimplement it.

Run the installed package through its portable wrapper; it derives its own
plugin root and sets `PYTHONPATH` correctly:

```bash
<plugin root>/scripts/run-hannah <path> [flags]
```

`<path>` defaults to `.` (the current repo). Requires Python ≥ 3.11.

## Flags

| Flag | Purpose |
| --- | --- |
| `--json` | Machine-readable output (schema `hannah/analysis@1`). Prefer this when you need to parse results. |
| `--track development\|inference\|general` | Optimization target (default `development`: coding assistants). |
| `--gpu vram=16gb,model=9070xt` | Override GPU detection. |
| `--ram 32gb` | Override system RAM. |
| `--no-color` | Plain output. |

Hardware is auto-detected on macOS (Apple Silicon → MLX) and Linux (AMD/NVIDIA →
ROCm/CUDA). On unsupported platforms or VMs, pass `--gpu`/`--ram` explicitly.

## How to interpret the result

Run with `--json` and read these fields:

- `repo.compound` / `repo.complexity_score` — how demanding the codebase is.
- `hardware.gpu_vram_gb`, `hardware.unified_memory`, `hardware.can_run_32b`,
  `hardware.max_recommended_quant` — the budget the models must fit.
- `recommendations[]` — already ranked best-first. `recommendations[0]` is P1.
  Each carries `name`, `size_gb`, `context_k`, `quant`, `mlx`, `tag`, `why`.

Then tell the user:

1. The **P1 pick** and the one-line reason (`why`).
2. The exact pull command, e.g. `ollama pull <name>` (drop any `-mlx` suffix and
   use the MLX runner instead when `mlx` is true on Apple Silicon).
3. One or two alternates (P2/P3) and when to prefer them (e.g. larger context,
   pure-coding focus).
4. If `recommendations` is empty, say so plainly and re-run with explicit
   `--gpu`/`--ram` overrides.

Keep advice concrete and honest: if a model will not fit, say it will not fit.
