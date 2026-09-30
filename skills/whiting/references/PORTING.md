# Port audit and provenance

Source: `lux-solari-codex-plugins`, revision
`ec05a1acebabd1759777312c303a609ba92e97b6`, plugin `whiting`.
Preserved source docs are audit records, not host-specific runtime instructions.

## Repairs

Merged inspect/repo-init/commit-conventions/semver-release now reference shipped helpers/templates. Inline approximate hooks replaced by canonical shipped sources. Working-agreement template no longer promises native Three Axes injection.

## Offline verification

Port Python suite: 46 tests passed before packaging relocation. Development
tests now live at repository-root `tests/whiting/`; run the repository's
`python scripts/run_checks.py` via `terminal`. Archived source docs live under
repository-root `provenance/whiting/source-skills/`, outside installed content.
Description: 57 characters, ending with a period;
Pitfalls and Verification sections present; literal shipped resource paths checked.

## Remaining limits

46 Python tests plus 3 shell suites passed. Initial tests inherited user tag.gpgsign=true and failed; per-process Git configuration isolation resolved it, without changing user configuration. No GitHub CI/release publishing or hook installation was executed.

## Maintenance workflow

Keep provenance unchanged; adapt active instructions to the flattened skill root.
Treat source commands as behavioral specifications, not registered host aliases.
Test canonical shipped helpers with disposable project fixtures and isolated user
configuration; report native hook and live-model/visual gaps separately.
