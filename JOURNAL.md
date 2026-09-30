# Journal

## 2026-09-29 — First release published and downloaded

- Independent review of the staged implementation returned no blocking security/logic issues. Baseline had 120 passing Python tests; the new suite has 129 passing tests and three passing shell suites. Review suggestions remain optional: exercise the root bump-helper copy directly and expand adjacent/missing changelog-section cases.
- Landed release machinery through checked PR #1 (https://github.com/luxsolari/lux-solari-hermes-plugins/pull/1); both branch/PR package checks passed. Whiting's bump helper suggested `v0.1.0`. Created and pushed an annotated tag on merged main commit `5e443cbf85706d02bbda46a2798c34805d445916` without moving any existing tag.
- Tag release workflow https://github.com/luxsolari/lux-solari-hermes-plugins/actions/runs/36661603932 passed and published https://github.com/luxsolari/lux-solari-hermes-plugins/releases/tag/v0.1.0. Manual retry https://github.com/luxsolari/lux-solari-hermes-plugins/actions/runs/36661694085 also passed; archive and checksum digests were unchanged.
- Downloaded both uploaded assets into scratch. `sha256sum --check SHA256SUMS` passed. The archive SHA-256 was `e9d7f1933668a2f1d02a97a24918407787790afc12263bd26572659ec54b295a`. All 257 tracked archive files matched tagged Git blob hashes, including 53 PNGs; archived VERSION was `0.1.0`. Published notes matched changelog extraction exactly; release is non-draft and non-prerelease.
- Open: Hannah's scanner blocker, live runtime parity checks, optional review test extensions, and upgrading template-derived action major versions. CI warns that checkout@v4/setup-python@v5 target deprecated Node 20; GitHub ran them on Node 24 successfully. Ubuntu-latest also carries a future image-migration notice. Local hooks are enabled only in this checkout; no server-side branch protection was added.
- Ruled out: mutating the published tag to include this later evidence entry, advertising tap installs as pinned releases, and treating a successful workflow as sufficient without downloading/readback.
- Files: `JOURNAL.md`; implementation files listed in the preceding entry. Release archives are under scratch, not tracked.

## 2026-09-29 — Whiting release machinery (publication pending)

- Added collection `VERSION` (initial `0.1.0`), a dated changelog, Whiting-derived working agreements, root hooks, changelog extractor and semantic-version suggestion helper. Enabled the hooks and protected default-branch setting only in this checkout's Git config.
- Added a tag/manual-dispatch Release workflow: canonical tag, tagged-tree identity, `main` ancestry, offline checks, matching VERSION/changelog gate, source archive/checksums, and GitHub Release publishing. Retries use the original tagged tree.
- Verified 129 Python tests and three shell suites with `.venv/bin/python scripts/run_checks.py`; new Python gates were exercised red/green for notes extraction, canonical tag syntax, version mismatch, and empty notes. Root hook tests exercised malformed/valid messages, protected main pushes, permitted branch and tag pushes. `python scripts/validate_release.py v0.1.0` emitted the dated release notes; `git diff --check` passed.
- Open: PR/remote CI and first release publication/readback. No live install rerun: runtime skill files did not change, and Hannah remains scanner-blocked.
- Ruled out: silently matching upstream component versions to the tap version, automatic unreviewed version bumps/tags, moving existing tags, rewriting pre-Whiting history, scan overrides, and calling local hooks server-side branch protection.
- Files: `AGENTS.md`, `VERSION`, `CHANGELOG.md`, `.github/workflows/release.yml`, `scripts/hooks/*`, `scripts/{extract_changelog,suggest_version_bump,validate_release}.py`, `tests/test_{release,repo_hooks}.py`, `README.md`.

## Publication and clean-home readback

- Changed: published the public Hermes sibling repository and documented the live install results.
- Verified: Hermes's actual tap enumerator discovers all nine names. Eight default installs succeeded in disposable `HERMES_HOME` directories; readback compared 184 installed files against the checkout by SHA-256 with no missing/changed files. This includes all visual assets. Code revision `baef023390d70eacbd3ee3acaa8b1dfe4deb31db` passed GitHub Actions run `36659606232`; local checks report 120 Python tests and three shell suites passing. All nine pass real frontmatter/support-parser checks. Eight scanner verdicts are `safe`, Hannah is `caution`.
- Open: Hannah's community-source install is blocked by the normal scanner; no override was applied. Source shell/git aliases are not native Hermes lifecycle registrations. Image generation, instructor behavior, Swiss rendered appearance, Windows/macOS execution, and installed Sage dev-test dotfile fixtures were not exercised. Existing installed skills were not replaced.
- Ruled out: GitHub's repository readback and Actions status—not a successful push alone—support publication/CI claims. Install return codes—notably zero on refusal—were not trusted without file readback.
- Files: `README.md`, `JOURNAL.md`, live smoke-test script; raw install/scanner results retained in session scratch rather than committed as stale generated reports.

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
