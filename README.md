# Lux Solari · Hermes ports

Hermes-native skill ports of [Lux Solari's Codex collection](https://github.com/luxsolari/lux-solari-codex-plugins), alongside the [Claude collection](https://github.com/luxsolari/lux-solari-plugins).

This repository is a **skill tap**, not a Codex/Claude marketplace manifest and not a collection of registered native Python plugins. Each skill includes its supporting files. Native tools or hooks belong in a later plugin package only when they need executable registration.

## Install

```sh
hermes skills tap add luxsolari/lux-solari-hermes-plugins
hermes skills search tri-swiss
hermes skills install luxsolari/lux-solari-hermes-plugins/skills/tri-swiss
```

Install another skill by replacing `tri-swiss` with its directory name below. The full identifier includes `skills/`. Adding a tap makes it discoverable; it does not install the collection. Installations go into the active Hermes profile and use Hermes's normal security scanner. The initial local scan reports eight `safe` verdicts and Hannah `caution` (including upstream privileged service-restart advice); asset-size findings remain visible for the visual skills. Review findings; do not disable scanning to make an installation pass.

Start a new session after installing. Invoke `/tri-swiss <request>`, or ask the agent to load the skill. Historical command names documented in source material are not automatically registered as independent Hermes commands.

## Collection

| Skill | Purpose |
| --- | --- |
| three-axes-framework | Behavioral calibration and collaboration discipline |
| sage-instructor | Explicit instructor mode, tracks, lessons, and progress |
| whiting | Repository setup, inspection, commits, and release discipline |
| hannah | Hardware-aware local-model recommendations; bundled Python engine |
| lux-swiss | Swiss visual system with ink, cream, and red |
| tri-swiss | Swiss visual system with a governed turquoise accent |
| anime-identity-designer | Anime identity art direction and image generation |
| lux-visual-systems | Lux Solari's editorial and image visual system |
| machine-pilgrim | Images grounded in Descent into the Machine canon |

## Boundaries

These are initial ports, not a certification of 1:1 runtime parity. Source hooks, marketplace launchers, and multi-command registrations do not become executable Hermes hooks merely by copying their prose. Skills provide on-demand instructions; they are not guaranteed global personality injection.

Hannah's engine ships inside its skill directory; see its prerequisites before invoking it. Visual skills ship the original reference PNGs and canon documents. They use Hermes image generation when a backend is available. Packaging tests do not prove image-provider availability, portrait fidelity, or pedagogical behavior.

Your currently installed skills are independent of this checkout. Creating this repository does not replace them.

## Development

Python 3.11+:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/run_checks.py
```

On Windows, activate `.venv\\Scripts\\Activate.ps1` instead. Tests check the nine-skill inventory, frontmatter, explicit support paths, image inventory, engine packaging, and repository hygiene. Read `JOURNAL.md` for execution evidence and remaining gaps.

`SOURCE.json` records the source revision and copied-file checksums. Original supporting material is retained where useful; historical source-command documents are references, not Hermes registrations.

## Licensing

Root code is MIT licensed. Per-skill `LICENSE`, `LICENSE-DESIGN`, and `NOTICE.md` files retain the upstream terms. **Do not assume the reference images, house marks, or design material are MIT licensed** just because the root code is. Read the relevant skill's terms before reuse.
