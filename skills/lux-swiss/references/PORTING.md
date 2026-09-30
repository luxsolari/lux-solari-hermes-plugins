# Port audit and provenance

Source: `lux-solari-codex-plugins`, revision
`ec05a1acebabd1759777312c303a609ba92e97b6`, plugin `lux-swiss`.
Preserved source docs are audit records, not host-specific runtime instructions.

## Repairs

Theme and component paths repaired; complete Tailwind-only block removal, font loading, heading font application, palette selection, and design-license boundaries clarified. Theme tokens unchanged.

## Offline verification

Port Python suite: 2 tests passed. Run via `terminal`
with this skill directory as workdir: `python3 -m unittest discover -s tests -v`.
Description: 51 characters, ending with a period;
Pitfalls and Verification sections present; literal shipped resource paths checked.

## Remaining limits

Static contracts only: no frontend build, font download, rendered browser checks, contrast audit, or automatic theme injection.

## Maintenance workflow

Keep provenance unchanged; adapt active instructions to the flattened skill root.
Treat source commands as behavioral specifications, not registered host aliases.
Test canonical shipped helpers with disposable project fixtures and isolated user
configuration; report native hook and live-model/visual gaps separately.
