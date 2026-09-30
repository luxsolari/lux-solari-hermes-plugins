<div align="center">
  <img src="assets/logo-vector.png" alt="Hannah — AI Strategy Engineer" />

  # Hannah

  [![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
  [![Version](https://img.shields.io/badge/version-0.7.3-informational.svg)](CHANGELOG.md)

  **The stopwatch doesn't lie. Neither does VRAM.**

  *Get your own local LLM strategy call.*
</div>

---

<img src="assets/logo-badge.png" alt="Hannah" align="right" width="280" />

Hannah is named after *[Hannah Schmitz](https://en.wikipedia.org/wiki/Hannah_Schmitz)*, the Red Bull Racing strategy engineer who calls the shots from the pit wall — the architect behind [Max Verstappen's record-breaking 2023 season](https://en.wikipedia.org/wiki/2023_Formula_One_World_Championship), in which he won 19 of 22 races and clinched the championship with six rounds to spare. This tool does the same for your LLM stack: it reads your codebase, measures your hardware, and returns a ranked podium of local models that will actually fit and perform — no guesswork, no yellow flags.

Scan a repo, read the garage, get the strategy call. In seconds.

<br clear="right" />

## Features

- 📊 **Circuit profiling** — scans your repo for languages, frameworks, and real line counts to score complexity on the Soft/Medium/Hard/Intermediate tyre scale
- ⛽ **Fuel Load** — estimates the token cost to load the entire repo into a model's context window; labels range from _featherweight_ to _overweight_ so you know before you prompt
- 🔩 **Spec detection** — identifies your tech stack (FastAPI, React, Vite, SQLAlchemy, etc.) from imports and manifests, not README prose
- 🔧 **Garage telemetry** — reads live hardware: Apple Silicon unified memory, AMD ROCm, NVIDIA CUDA
- 🏎️ **Strategy matching** — maps complexity tier + VRAM budget to a curated model catalog
- 🏆 **Ranked podium (P1–P5)** — exact `ollama pull` commands, VRAM cost, and context window for each pick
- ✅ **Live garage inventory** — queries your local Ollama instance; already-pulled models are promoted to _ready to race_ with a `✅` badge; everything else gets a `⬇️ pull required` tag
- 🚫 **DNF flags** — models that won't fit are called out directly; no "it might work if you close Chrome"
- 🍎 **Apple MLX support** — recommends MLX-optimised variants automatically on Apple Silicon
- 🤖 **Machine-readable output** — `--json` emits `schema: hannah/analysis@1` for CI/CD pipelines and agent consumption
- 🔌 **Three surfaces** — standalone CLI, `/hannah` slash command in Claude Code/Cowork, or portable skill file for Codex, ChatGPT, Qoder, Hermes, and others

## Quick Start

Hannah ships as a zero-dependency, pure-stdlib engine (Python ≥ 3.11). Three ways to run it:

### Standalone CLI

```bash
# Install once
pip install -e .

# Analyze current directory
python3 -m hannah

# Analyze a specific repo with overrides
python3 -m hannah /path/to/repo --gpu vram=16gb --ram 64gb

# Machine-readable output for pipelines
python3 -m hannah --json
```

### Precompiled installer (macOS / Windows)

Download the `.pkg` (macOS, Apple Silicon) or `.msi` (Windows, x64) from the [Releases page](https://github.com/luxsolari/hannah/releases) — no Python required.

These installers are **unsigned**, so your OS will warn you on first run:

- **macOS**: Gatekeeper blocks the `.pkg` with "Apple could not verify this app is free of malware." Right-click the file and choose **Open** (instead of double-clicking), or run `xattr -d com.apple.quarantine hannah-*.pkg` before installing.
- **Windows**: SmartScreen shows "Windows protected your PC." Click **More info → Run anyway**.

Once installed, `hannah` is on your `PATH` — run it from any terminal.

### Claude Code / Cowork plugin

Install via the marketplace, then run:

```
/hannah:strategy
```

Hannah will analyze the active workspace and return the strategy call inline.

### Portable skill (Codex, ChatGPT, Qoder, Hermes, ...)

Point any skill-aware agent at [`skills/hannah/SKILL.md`](skills/hannah/SKILL.md). The skill shells out to `python3 -m hannah` and interprets the JSON output. The only prerequisite is Python ≥ 3.11 and the `hannah` package on `PYTHONPATH` — clone this repo or `pip install -e .`.

## Flags

| Flag | Purpose |
|---|---|
| `--track development\|inference\|general` | Optimization target (default: `development`) |
| `--gpu vram=16gb,model=9070xt` | Override GPU detection |
| `--ram 32gb` | Override system RAM |
| `--json` | Emit machine-readable JSON (`schema: hannah/analysis@1`) |
| `--no-color` | Plain text output for piping or logging |

## Example Output

```
🏁 HANNAH RACE CONTROL — REPOSITORY ANALYSIS COMPLETE
═══════════════════════════════════════════════════════
📊 Circuit: console-jack
🏎️  Chassis: Java + Markdown + JSON
🔩 Spec: none detected
⛽ Fuel Load: ~670K tokens (heavy — requires 128K+ context)
🔧 Tyre Compound: Hard (complexity 7.2/10, ~67K lines / 312 files)

💻 Garage: Apple M1 Pro · 16GB unified · mlx
   Unified memory — RAM doubles as the VRAM pool
   Quant ceiling: q5_k_m · 32B-class viable: yes

🏆 PODIUM RECOMMENDATIONS  (development track)
═══════════════════════════════════════════════════════
🥇 P1 — ✅ gemma4:12b-mlx (10.0 GB, 128K ctx) [MLX optimized · ready to race]
🥈 P2 — ⬇️  qwen2.5-coder:14b-q4_k_m (8.2 GB, 128K ctx) [Fits in VRAM · pull required]
🥉 P3 — ✅ qwen3.5:9b-mlx (8.9 GB, 256K ctx) [MLX optimized · ready to race]

📋 RACE NOTES
- Ollama config: num_gpu=999, flash_attention=1
- Suggested context window: 256K
═══════════════════════════════════════════════════════
"Data is clean. Go win the championship."
```

## Tests

```bash
python3 -m unittest discover -s tests
```

## Contributing & Roadmap

See [ROADMAP.md](ROADMAP.md) for planned features and how to contribute.

## License

MIT
