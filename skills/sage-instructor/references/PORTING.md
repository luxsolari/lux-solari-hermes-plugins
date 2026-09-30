# Port audit and provenance

Source: `lux-solari-codex-plugins`, revision
`ec05a1acebabd1759777312c303a609ba92e97b6`, plugin `sage-instructor`.
Preserved source docs are audit records, not host-specific runtime instructions.

## Repairs

Project-local learner state/custom curricula, bundled-track fallback, official-doc grounding, ownership review, exact topic keys, phase-recalibration progression, and canonical checker paths restored.

## Offline verification

Port Python suite: 11 tests passed. Run via `terminal`
with this skill directory as workdir: `python3 -m unittest discover -s tests -v`.
Description: 57 characters, ending with a period;
Pitfalls and Verification sections present; literal shipped resource paths checked.

## Remaining limits

Offline tests do not exercise a live instructor or scenario conversations. Question-tool availability varies; ordinary-chat choices are the fallback. No registered command aliases or automatic state updater.

## Maintenance workflow

Keep provenance unchanged; adapt active instructions to the flattened skill root.
Treat source commands as behavioral specifications, not registered host aliases.
Test canonical shipped helpers with disposable project fixtures and isolated user
configuration; report native hook and live-model/visual gaps separately.
