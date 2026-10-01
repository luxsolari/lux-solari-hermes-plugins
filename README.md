# Lux Solari · Hermes ports

[![Release](https://img.shields.io/github/v/release/luxsolari/lux-solari-hermes-plugins)](https://github.com/luxsolari/lux-solari-hermes-plugins/releases)
[![License](https://img.shields.io/badge/code-MIT-blue)](LICENSE)
[![Checks](https://github.com/luxsolari/lux-solari-hermes-plugins/actions/workflows/test.yml/badge.svg)](https://github.com/luxsolari/lux-solari-hermes-plugins/actions/workflows/test.yml)

Hermes-native skills, including [Bauer](https://github.com/luxsolari/bauer), and ports of [Lux Solari's Codex collection](https://github.com/luxsolari/lux-solari-codex-plugins), alongside the [Claude collection](https://github.com/luxsolari/lux-solari-plugins).

This repository is a **skill tap**, not a Codex/Claude marketplace manifest and not a collection of registered native Python plugins. Each skill includes its supporting files. Native tools or hooks belong in a later plugin package only when they need executable registration.

## Install

```sh
hermes skills tap add luxsolari/lux-solari-hermes-plugins
hermes skills search tri-swiss
hermes skills install luxsolari/lux-solari-hermes-plugins/skills/tri-swiss
```

Install another skill by replacing `tri-swiss` with its directory name below. The full identifier includes `skills/`. Adding a tap makes it discoverable; it does not install the collection. Installations go into the active Hermes profile and use Hermes's normal security scanner. The current local scan reports nine `safe` verdicts (including Bauer) and Hannah `caution` (including upstream privileged service-restart advice). **Hermes blocks Hannah's default community-source installation at that verdict; it remains a published port with an installation blocker, not a clean-install claim.** Asset-size findings remain visible for the visual skills. Review findings; do not disable scanning to make an installation pass.

Start a new session after installing. Invoke `/tri-swiss <request>`, or ask the agent to load the skill. Historical command names documented in source material are not automatically registered as independent Hermes commands.

## Collection

| Skill | Purpose |
| --- | --- |
| three-axes-framework | Behavioral calibration and collaboration discipline |
| sage-instructor | Explicit instructor mode, tracks, lessons, and progress |
| whiting | Repository setup, inspection, commits, and release discipline |
| hannah | Hardware-aware local-model recommendations; bundled Python engine |
| bauer | Evidence-backed OWASP security audits, advisory and supply-chain review |
| lux-swiss | Swiss visual system with ink, cream, and red |
| tri-swiss | Swiss visual system with a governed turquoise accent |
| anime-identity-designer | Anime identity art direction and image generation |
| lux-visual-systems | Lux Solari's editorial and image visual system |
| machine-pilgrim | Images grounded in Descent into the Machine canon |

## Boundaries

These are initial ports, not a certification of 1:1 runtime parity. Source hooks, marketplace launchers, and multi-command registrations do not become executable Hermes hooks merely by copying their prose. Skills provide on-demand instructions; they are not guaranteed global personality injection.

Hannah's engine ships inside its skill directory; see its prerequisites before invoking it. Visual skills ship the original reference PNGs and canon documents. They use Hermes image generation when a backend is available. Packaging tests do not prove image-provider availability, portrait fidelity, or pedagogical behavior.

Bauer v0.1.0 ships unchanged from its canonical repository with four standard-library Python helpers and five references. It is an agent-driven audit workflow, not an autonomous scanner or security certification. Dependency inventory disclosure and optional TypeSafe/Jev evidence review require explicit consent; no remote queries run during packaging checks. Its OSV helper fails closed on RFC3339 leap-second timestamps (`:60`); such responses remain incomplete, not zero-finding results.

Your currently installed skills are independent of this checkout. Creating this repository does not replace them.

## Development

Python 3.11+:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/run_checks.py
```

On Windows, activate `.venv\\Scripts\\Activate.ps1` instead. Tests check the ten-skill inventory, frontmatter, explicit support paths, image inventory, engine packaging, and repository hygiene. Read `JOURNAL.md` for execution evidence and remaining gaps.

`SOURCE.json` records the original collection source revision and checksums; `additional_sources.bauer` pins Bauer’s independent canonical revision and checksums for all ten skill files plus its per-skill license and notice. Bauer’s source-parity tests verify exact packaged bytes against those pinned digests. Original supporting material is retained where useful; historical source-command documents are references, not Hermes registrations.

## Releases and Whiting

Collection versions live in `VERSION`; inherited skill and engine versions remain independent. Release notes come from the matching version section in `CHANGELOG.md`, not generated commit summaries. The release archive contains the full tracked repository, including the original notices and reference assets.

Activate Whiting's repository-local hooks after cloning:

```sh
git config core.hooksPath scripts/hooks
git config whiting.defaultbranch main
```

The hooks reject malformed commit subjects and direct pushes to `main`. They allow feature branches and release tags. They are local guardrails, not GitHub branch protection; server-side protection is not configured by this repository.

Use `/whiting semver-release` (or ask the agent to load `whiting` and follow its release procedure). The maintainer sequence is:

1. Run `python scripts/suggest_version_bump.py` and review its recommendation.
2. On a branch, update `VERSION`, move the selected changes from `[Unreleased]` into a dated changelog section, and run `python scripts/run_checks.py` plus `python scripts/validate_release.py vX.Y.Z`.
3. Open a PR and merge it after the checks pass.
4. Fetch the merged `main`, create an annotated `vX.Y.Z` tag on that exact commit, and push the tag. Do not move an existing release tag.

The Release workflow checks the tag's identity and ancestry on `main`, reruns offline tests, checks version and notes, then publishes a GitHub Release with a `.tar.gz` source archive and `SHA256SUMS`. A manual dispatch with an existing tag can retry publication; it uses the tagged tree, not the current branch, and replaces that tag's assets. It does not automatically bump versions or create tags.

Tagged archives are release snapshots. Normal Hermes tap installations still follow the repository's default branch; creating a release does not pin or upgrade installed skills.

## Verification status

- The local ten-skill inventory passes packaging checks. Hermes’s actual frontmatter validator and support parser accept all ten; the community-source scanner returns nine `safe` verdicts and Hannah `caution`. Bauer’s informational API-key-read finding remains visible. Remote tap discovery was previously verified for the original nine; Bauer’s remote discovery/install is pending publication.
- 132 Python tests and three Whiting shell suites passed locally, including Bauer’s inventory, pinned-source byte parity, and four helper CLI help checks. Remote CI evidence for the previous release is recorded in `JOURNAL.md`.
- Eight default installations were exercised in disposable Hermes homes. SHA-256 readback matched 184 installed files to the checkout, including all 53 reference PNGs.
- Hannah was fetched and scanned but **not installed**: the normal community-source scan blocks its `caution` verdict. The live smoke-test command therefore exits non-zero until that blocker is resolved.
- No existing installed skills were replaced. No live image generation, instructor conversation, or Swiss browser rendering was tested.

For a networked installation/readback check (requires Hermes and authenticated `gh` for reliable GitHub API capacity):

```sh
python scripts/test_install.py
```

## Licensing

Root code is MIT licensed. Per-skill `LICENSE`, `LICENSE-DESIGN`, and `NOTICE.md` files retain the upstream terms. **Do not assume the reference images, house marks, or design material are MIT licensed** just because the root code is. Read the relevant skill's terms before reuse.
