# Port audit and provenance

Historical initial port source: `lux-solari-codex-plugins`, revision
`ec05a1acebabd1759777312c303a609ba92e97b6`, plugin `three-axes-framework`.
Preserved source docs are audit records, not host-specific runtime instructions.

## Repairs

Conversational setup/status/presets/recovery, profile scope, all thirteen Integrity Rules and signal durations preserved. Presets compared to retained source commands.

## Offline verification

Port Python suite: 3 tests passed. Run via `terminal`
with this skill directory as workdir: `python3 -m unittest discover -s tests -v`.
Description: 54 characters, ending with a period;
Pitfalls and Verification sections present; literal shipped resource paths checked.

## Remaining limits

Three original Node suites passed 20 tests against the upstream hooks only; those hooks are not shipped here. No native lifecycle injection, denial gate, or startup clearing; assistant routing and ephemeral session state are conversational.

## Maintenance workflow

Keep initial collection provenance unchanged. Current released open-source binding and hashes are maintained in `maintenance/three-axes/release.json` at the tap root and `SOURCE.json` additional_sources.three-axes-framework. Adapt active instructions to the flattened skill root.
Treat source commands as behavioral specifications, not registered host aliases.
Test canonical shipped helpers with disposable project fixtures and isolated user
configuration; report native hook and live-model/visual gaps separately.
