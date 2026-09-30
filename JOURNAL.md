# Journal

## Initial Hermes skill-tap packaging

- Changed: created the nine-skill tap, restored references, curricula, scripts, Hannah's Python package, CSS and 53 reference PNGs; retained per-skill design licenses/notices. Audited Hermes tool guidance, paths, descriptions, platform gates, and conversational routing. Added README, source provenance checksums, offline tests, and GitHub Actions.
- Verified: `python scripts/run_checks.py` returned 119 passing Python tests and three passing Whiting shell suites in isolated Git configuration. Hermes's real frontmatter validator accepted all nine. Hermes's real skill scanner returned eight `safe` verdicts and Hannah `caution`; no `dangerous` skill verdicts after separating Whiting's development tests and historical Codex instructions from installed content. Image assets retain original bytes.
- Open: remote publication, tap discovery, clean-home installation/readback, remote CI; live image generation, instructor conversations, Swiss browser rendering, and native lifecycle/alias parity are not exercised.
- Ruled out: wrapping every skill as a Python plugin adds no behavior. No scanner disabling, scan-ignore tricks, fabricated native hooks, or edits to currently installed skills. Whiting source prose and tests belong in repository provenance/development directories, not active skill instructions.
- Files: `skills/*/SKILL.md`, `tests/test_tap.py`, `tests/whiting/`, `scripts/run_checks.py`, `scripts/hermes_probe.py`, `.github/workflows/test.yml`, `SOURCE.json`, per-skill `references/PORTING.md`, `provenance/whiting/`.
