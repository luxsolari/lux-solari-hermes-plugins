# Journal

## Live installer boundary audit

- Changed: replaced directory-only support references in Three Axes/Whiting with explicit files or unambiguous target-project paths. Real GitHubSource fetch rejected tree-directory entries as non-regular referenced files despite valid local frontmatter; the CLI mislabeled this as a stale index. Added actual support-parser checks to the probe and reused existing gh authentication without persisting credentials.
- Verified: first clean-home pass downloaded six skills byte-for-byte, including all 53 PNGs and visible Sage snapshot. Retried Three Axes/Whiting and traced rejection to the directory references, not missing upstream files or GitHub rate limits. Remote CI for prior code revision passed.
- Open: clean-home readback after directory-reference repair; Hannah remains blocked with community-source `caution` (upstream service-management advice). No `--force` or trust/scanner bypass applied. Live visual/instructor behavior and native hook registrations remain unverified.
- Ruled out: successful CLI exit code alone proves nothing: Hermes returned zero for scan-blocked and fetch-failed installs. Smoke tests require exact installed-file readback instead.
- Files: `scripts/hermes_probe.py`, `scripts/test_install.py`, Three Axes/Whiting skill bodies, `README.md`.

## Tap-download boundary regression

- Changed: renamed Sage's hidden upstream snapshot to a visible filename and updated checker/test paths; Hermes's GitHub bundler excludes dotfiles. Added a regression test and live clean-home installer smoke test.
- Verified: initial GitHub publication read back as public with `main` at `5e3211e6d263a85e5f43b284ce11a6e9c8d452d1`; initial remote Actions run `36658737927` succeeded. A disposable home's tap add/list resolves the source path as `skills/`.
- Open: live all-skill install/readback and final-revision CI still pending at this commit.
- Ruled out: keeping a required runtime snapshot as a dotfile silently drops it during download; renaming is preferable to changing Hermes's installer exclusions. Original source/canon whitespace remains intact.
- Files: `skills/sage-instructor/scripts/check_framework_drift.py`, its visible reference snapshot and regression tests, `scripts/test_install.py`, `tests/test_tap.py`.

## Initial Hermes skill-tap packaging

- Changed: created the nine-skill tap, restored references, curricula, scripts, Hannah's Python package, CSS and 53 reference PNGs; retained per-skill design licenses/notices. Audited Hermes tool guidance, paths, descriptions, platform gates, and conversational routing. Added README, source provenance checksums, offline tests, and GitHub Actions.
- Verified: `python scripts/run_checks.py` returned 119 passing Python tests and three passing Whiting shell suites in isolated Git configuration. Hermes's real frontmatter validator accepted all nine. Hermes's real skill scanner returned eight `safe` verdicts and Hannah `caution`; no `dangerous` skill verdicts after separating Whiting's development tests and historical Codex instructions from installed content. Image assets retain original bytes.
- Open: remote publication, tap discovery, clean-home installation/readback, remote CI; live image generation, instructor conversations, Swiss browser rendering, and native lifecycle/alias parity are not exercised.
- Ruled out: wrapping every skill as a Python plugin adds no behavior. No scanner disabling, scan-ignore tricks, fabricated native hooks, or edits to currently installed skills. Whiting source prose and tests belong in repository provenance/development directories, not active skill instructions.
- Files: `skills/*/SKILL.md`, `tests/test_tap.py`, `tests/whiting/`, `scripts/run_checks.py`, `scripts/hermes_probe.py`, `.github/workflows/test.yml`, `SOURCE.json`, per-skill `references/PORTING.md`, `provenance/whiting/`.
