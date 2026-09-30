# Regression harness

Sage's "source code" is natural-language instructions (`SKILL.md`, `curricula/*.md`)
interpreted by an LLM at runtime, not a program you can unit-test in the usual
sense. This harness makes regression testing repeatable anyway, split into two
tiers:

## Tier 1 — deterministic structural checks

`check_progress_schema.py` validates a `.sage-progress.json` (and the presence
of `.sage-profile.md`) against the rules in `SKILL.md`'s Progress Rules
section — kebab-case topic keys (Rule 10), mutually-exclusive hint streaks
(Rule 8), `review_due` staying a subset of `topic_confidence`, observations
length, exercise slug format, profile file location. No LLM involved; runs in
milliseconds; wired into CI on every push and PR
(`.github/workflows/tier1-checks.yml`).

```
python3 tests/check_progress_schema.py <path-to-a-project-dir-with-.sage-progress.json>
```

This catches schema drift (an artifact malformed relative to the spec) but
says nothing about whether Sage's *behavior* was pedagogically correct — that
needs Tier 2.

### Testing the checker itself

`check_progress_schema.py` is plain deterministic code, so it gets its own
unit tests rather than relying on an expensive Tier 2 run to notice a bug in
it (that's exactly how the `next_up`/`warn()` bug shipped originally — see
`CHANGELOG.md`). `test_check_progress_schema.py` runs the checker against the
fixtures in `fixtures/` (`valid/`, `valid-track-complete/`, and several
`invalid-*/` directories each isolating one violation) and pins the expected
exit code and failure message per fixture:

```
python3 tests/test_check_progress_schema.py -v
```

This is what `.github/workflows/tier1-checks.yml` runs on every push and PR
against `main` — Tier 1 is the actual automated gate; Tier 2 remains manual
(see below).

## Tier 2 — scripted behavioral scenarios

`scenarios/*.md` are fixed, repeatable session scripts — not open-ended
"go explore" prompts. Each one targets a specific bug class that was
previously found and fixed (see `CHANGELOG.md` 1.2.0), so re-running them
after a `SKILL.md` or curriculum edit tells you whether that fix still holds.

Each scenario file has:
- **Regression target** — the specific bug this guards against, with a
  `SKILL.md` line reference.
- **Setup** — the scratch project state to start from.
- **Script** — a fixed sequence of learner turns/commands. Not improvised.
- **Assertions** — a checklist split into `[mechanical]` (checkable by
  `check_progress_schema.py` or by grepping the transcript for a literal) and
  `[behavioral]` (requires reading the transcript and judging intent).

### Running a scenario

There's no separate test-runner binary — the "test runner" is an agent that
plays both Sage (per the current `SKILL.md`/`curricula/`) and the scripted
learner persona, executing real commands where the spec calls for real
execution (Step 6b `verify`), then grades itself against the scenario's
assertion checklist. `run_scenario_prompt.md` is the reusable prompt template
for that agent.

Use it via Claude Code's `Agent` tool (or paste it into a fresh session):

1. Give the agent `run_scenario_prompt.md`'s contents with `{SCENARIO}`
   substituted for a path under `tests/scenarios/`.
2. It works in an isolated scratch directory (never inside this repo), reads
   the relevant `SKILL.md`/curriculum sections directly (not from memory),
   executes the script turn by turn, and produces a transcript plus real
   `.sage-progress.json` / `.sage-profile.md` artifacts.
3. It runs `check_progress_schema.py` against those artifacts for the
   mechanical assertions and self-grades the behavioral ones, citing the
   specific transcript line and `SKILL.md` rule for each.
4. It reports PASS/FAIL per assertion — not a vibe summary.

### Why Tier 2 isn't wired into CI

Each scenario run is a multi-turn LLM conversation that costs real tokens and
minutes, and the "system under test" and the "test runner" are both LLMs
interpreting a spec, so results aren't bit-for-bit deterministic the way a
unit test is. Tier 2 is a **pre-release gate**, run manually, not a
per-commit CI check.

### Pre-release checklist

Before bumping the plugin version (`.claude-plugin/plugin.json` +
`CHANGELOG.md`), run **all ten** scenarios in `scenarios/` — not just the
ones nearest whatever you changed. Record the result (pass/fail per
assertion) in the version's CHANGELOG entry the way 1.2.0 and the harness's
own rollout did, so "we ran the harness" is checkable later instead of
trusted on faith. If a scenario fails, that's either a spec bug (fix
`SKILL.md`/the curriculum) or a scenario gone stale (the curriculum changed
underneath it — update the scenario's setup/script to match).

### Adding a scenario

When a live-session bug hunt (like the ones behind 1.2.0) finds something new
and it gets fixed in `SKILL.md`, add a scenario file here targeting it, so the
next spec edit gets checked against it instead of relying on someone
remembering to re-discover the same bug.
