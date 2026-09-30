# Scenario 04 — Hint-streak wording and decline-resets-streak

## Regression target
- The recalibration offer must be worded as "the last few exercises," never
  "this phase" — the streak is exercise-scoped and can span a phase boundary.
  See `SKILL.md` Phase transitions section (the paragraph right after the
  four standard options) and Axis Re-Calibration.
- Declining the offer must reset the streak that triggered it, so it doesn't
  resurface at every subsequent phase transition — but a *fresh* streak that
  accumulates afterward earns a genuinely new offer. See `SKILL.md` Axis
  Re-Calibration, the "if the learner declines" bullet.

## Setup
Scratch directory with `.sage-progress.json`:
```json
{
  "active_track": "python-basics",
  "tracks": {
    "python-basics": {
      "phase": 0,
      "completed_exercises": ["P0-fizzbuzz"],
      "current_topic": "Control flow",
      "current_exercise": "P0-temp-converter",
      "next_up": "P0-word-counter",
      "observations": "",
      "topic_confidence": {},
      "review_due": [],
      "axis_overrides": {},
      "low_hint_streak": 0,
      "high_hint_streak": 1,
      "last_session": "",
      "hint_count": 0
    }
  }
}
```
(`high_hint_streak: 1` simulates that `P0-fizzbuzz` already needed 3+ hints.)
Valid `.sage-profile.md`.

## Script
1. Learner works `P0-temp-converter`, needs 3+ hints (drive `hint_count` to
   3 via real `/sage-hint` calls), then submits a correct solution. Verify
   passes. `high_hint_streak` should become 2 — this exercise is **not** the
   end of Phase 0 (one more, `P0-word-counter`, remains), so no phase
   transition happens here, but the recalibration threshold (`>= 2`) is now
   met.
2. Learner works `P0-word-counter` (Phase 0's last exercise), needs 3+ hints
   again, submits a correct solution. Verify passes. This IS the end of
   Phase 0 → the phase-transition AskUserQuestion fires.
3. At the phase-transition question, the recalibration option should be
   present (per the streak state) — check its exact wording.
4. Learner picks a **non-recalibration** option ("Save checkpoint and stop
   for now"), i.e. declines the offer.
5. Learner starts Phase 1, completes `P1-list-ops` needing 3+ hints again.
6. Learner completes `P1-comprehension-refactor` (Phase 1's *second* of
   three exercises — `P1-list-ops`, `P1-comprehension-refactor`,
   `P1-json-roundtrip`, per `curricula/python-basics.md` — not its last),
   also needing 3+ hints. `high_hint_streak` reaches the `>= 2` threshold
   here, but this is **not** a phase-transition point.
7. Learner completes `P1-json-roundtrip` (Phase 1's actual last exercise),
   again needing 3+ hints so the streak isn't reset by a hint-free pass.
   This IS the end of Phase 1 → the phase-transition AskUserQuestion fires.

## Assertions

- `[behavioral]` The recalibration option's wording at step 3 says "the last
  few exercises" (or clearly equivalent phrasing that doesn't scope to a
  single phase) — quote it directly. It must not say "this phase" given the
  streak spans `P0-temp-converter` and `P0-word-counter`, both inside Phase
  0 here, but the copy itself must be the phase-agnostic wording regardless
  of whether this particular run happens to stay within one phase.
- `[mechanical]` After step 4 (decline), `high_hint_streak` is reset to `0`
  in the progress file — diff before/after the decline.
- `[behavioral]` After step 5 (first Phase 1 struggle exercise post-decline),
  no recalibration offer fires yet — the streak was reset in step 4, so this
  is only the first struggle exercise of a new streak (`high_hint_streak ==
  1`), below threshold.
- `[behavioral]` After step 6, `high_hint_streak == 2` (threshold met) but
  **no** recalibration offer is presented — `P1-comprehension-refactor` is
  not Phase 1's last exercise, so no phase-transition question fires at all
  here, and per SKILL.md (Axis Re-Calibration: "Both signals are only
  checked at phase-transition points") the signal isn't surfaced outside
  one. Sage should show only the standard 4-option "Exercise complete. What
  next?" menu, with no 5th option.
- `[behavioral]` After step 7 (Phase 1's actual last exercise, phase
  transition fires), `high_hint_streak == 3` and a **fresh** recalibration
  offer is presented at the phase-transition question — confirm this isn't
  suppressed as a repeat of the declined one (SKILL.md: "a fresh streak
  accumulating from here is a new signal and earns a fresh offer").
- `[mechanical]` `python3 tests/check_progress_schema.py <scratch-dir>` exits
  0 at every checkpoint.
