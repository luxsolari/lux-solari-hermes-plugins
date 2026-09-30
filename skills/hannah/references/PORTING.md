# Port audit and provenance

Source: `lux-solari-codex-plugins`, revision
`ec05a1acebabd1759777312c303a609ba92e97b6`, plugin `hannah`.
Preserved source docs are audit records, not host-specific runtime instructions.

## Repairs

Shipped engine documented at skill root, missing packaging README supplied, local-package install instructions verified in an isolated scratch venv. Actual CLI pipeline exercised with external metadata mocked and network denied. Engine runtime source is unchanged.

## Offline verification

Port Python suite: 49 tests passed. Run via `terminal`
with this skill directory as workdir: `python3 -m unittest discover -s tests -v`.
Description: 58 characters, ending with a period;
Pitfalls and Verification sections present; literal shipped resource paths checked.

## Remaining limits

The package built/installed as 0.10.6; only packaging dependencies were downloaded, never model weights. Upstream oversized/platform-incompatible fallback, approximate catalog data/benchmark mappings, and summed VRAM remain fidelity gaps documented in Pitfalls. No model availability, inference, or performance testing.

## Maintenance workflow

Keep provenance unchanged; adapt active instructions to the flattened skill root.
Treat source commands as behavioral specifications, not registered host aliases.
Test canonical shipped helpers with disposable project fixtures and isolated user
configuration; report native hook and live-model/visual gaps separately.
