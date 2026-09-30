# Three Axes calibration contract

General behavioral baseline: **defaults → global → project → session**.
Defaults: `mastery=medium`, `consequence=medium`, `intent=balanced`. Global profile
is `three-axes-profile.json` under `HERMES_HOME` (fallback `~/.hermes`), project
profile is `.three-axes.json`; session overrides are conversation state, not a
shared file. Load Three Axes when available and follow its conversational setup
and validation; no lifecycle enforcement or Codex-home migration is installed.

For teaching, the active curriculum declares the track's axes; its persisted
`tracks.<id>.axis_overrides` wins over those declarations. Task-scoped signals
can temporarily narrow the teaching behavior without rewriting either source.
If Three Axes is unavailable, use this contract plus `philosophy.md` for lesson
depth, hint escalation, and verification strictness. `.sage-profile.md` and
`.sage-progress.json` at the learner project root own learner and track state.
