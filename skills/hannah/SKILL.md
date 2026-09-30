---
name: hannah
description: "Recommend local LLM models for your codebase and hardware."
version: 1.7.0
author: Lux Solari (luxsolari), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [local-llm, model-recommendation, ollama, hardware-analysis, repo-analysis, mlx]
    related_skills: []
---
# Hannah — F1 Strategy Engineer for Your LLM Garage

Analyze a repo and host hardware with the shipped stdlib Python engine, then
rank local model candidates as a podium. Rankings are heuristics, not guarantees
of availability, memory fit, speed, benchmark validity, or model quality.

## When to Use

- Choose an Ollama/Apple-MLX model for a repo and the available hardware.
- Inspect language/framework mix, estimated context needs, and VRAM/RAM limits.

## Prerequisites and Installation

Python 3.11+. The engine (`hannah/`) and `pyproject.toml` live directly in this
skill root. Resolve `<skill-root>` from the loaded SKILL.md. **Do not run
`pip install hannah` from PyPI**: install this shipped package, not a namesake.
No third-party runtime dependencies are needed. Packaging uses setuptools/wheel.

Use `terminal` with this skill root as `workdir` for the no-install invocation:

```sh
python3 -m hannah "<absolute-target-repo>" --json --gpu vram=16gb,model=9070xt --ram 32gb
```

POSIX helper, callable from any target repo:

```sh
sh "<skill-root>/scripts/run-hannah" "<absolute-target-repo>" --json
```

Or install into an explicit venv (outside the skill's source files):

```sh
python3 -m venv "<venv-path>"
"<venv-path>/bin/python" -m pip install "<skill-root>"
"<venv-path>/bin/python" -m hannah "<absolute-target-repo>" --json
```

Windows: use `py -3 -m venv "<venv-path>"` and
`"<venv-path>\Scripts\python.exe" -m pip install "<skill-root>"`, then that
interpreter's `-m hannah`. Do not use the POSIX wrapper on native Windows.
Install/build may need network for packaging tools; running the module from
skill-root needs no package install.

## How to Run and Interpret

Use `terminal` to execute the engine; never reimplement its analyzer/ranking.
Target path defaults to `.` in the invocation workdir, not necessarily the user
repo. `--help` / `--version` are safe no-analysis smoke checks.

| Flag | Meaning |
| --- | --- |
| --json | Schema `hannah/analysis@1`; use for grounded report rendering. |
| --track development / inference / general | Optimization target; development default. |
| --gpu vram=16gb,model=9070xt | Integer-GB manual override. |
| --ram 32gb | Integer-GB RAM override. |
| --no-color | Disable console colors. |

macOS/Linux hardware probes are best-effort. Native Windows/VMs should provide
explicit overrides. An override replaces detection with `platform=manual`; it
is not an additive correction, and will not enable Apple-MLX platform selection.

Read `repo` (complexity score **0–10**, compound, language/framework mix, token
estimate), `hardware` (notes and budgets), `recommendations` (already ranked),
`discoveries` (unscored local/library candidates), and `race_notes`.
The `context_k` field contains **token counts**, despite its name; divide by
1000 when rendering K-context. No dependency count, test-coverage measurement,
AST complexity, quantization retuning, or performance benchmark is performed.

Render the full F1 Race Control report using `references/strategy.md`, including
all supplied recommendations/discoveries/race notes. If JSON was requested,
return the actual raw JSON instead. Keep the final strategy summary short:
P1's actual reason, when to use an alternate, and verified runner/pull guidance.
Use `ollama pull <exact-name>` only for a confirmed Ollama tag and never download
models without approval. MLX catalog names ending `-mlx` are labels, not verified
Hugging Face repository IDs; identify a real compatible repo/runner first rather
than stripping a suffix and promising it runs.

## Pitfalls

- Normal analysis calls the local Ollama API, scans Ollama's web library, and
  fetches/caches benchmark metadata. It does **not** pull model weights, but is
  not offline; there is no `--offline` flag. Use the mocked offline CLI test below
  for deterministic exercise without network, cache writes, or downloads.
- The upstream registry may allow partial offload, admit Apple candidates without
  a size check, or fall back to its first three catalog entries when no candidate
  fits. Therefore a nonempty podium (or “Fits in VRAM” tag) is not proof of fit.
  Independently compare size, RAM/VRAM, KV-cache/context overhead, and platform;
  flag mismatches instead of presenting impossible candidates as runnable.
- Catalog names, sizes, and benchmark ID mappings can be stale or approximate.
  Distinguish fetched results from catalog estimates and unscored discoveries.
- Summed multi-GPU VRAM does not guarantee any runner can split the model.
- A pulled model means installed in Ollama, not exercised successfully. Verify
  runtime before calling it usable. Model choice still needs workload testing.
- `references/source-SKILL.md` preserves upstream instructions; this file and
  the adapted strategy reference govern paths/tools in Hermes.

## Verification

Through `terminal` with skill-root as `workdir`:

```sh
python3 -m hannah --help
python3 -m hannah --version
python3 -m unittest discover -s tests -v
```

The offline CLI regression test calls the real argument parser, repo analyzer,
registry, and reporters while mocking external metadata and denying network.
Parse real JSON and check schema/ranks/path. For normal analysis, report probe
limits and independently check fit before recommending; read back any externally
changed state. Do not claim inference quality or model availability was tested
by this offline suite.
