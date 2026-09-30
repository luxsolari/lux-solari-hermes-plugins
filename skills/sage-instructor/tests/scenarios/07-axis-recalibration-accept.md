# Scenario 07 — Axis re-calibration accept path

## Regression target
- The recalibration offer's **accept** branch has never been live-tested.
  Scenario 04 only exercises decline. This scenario triggers `low_hint_streak
  >= 3` (the "Mastery is probably too low" signal) and has the learner
  **accept** the bump, checking that: `axis_overrides` gets the new level
  (never the curriculum file itself), a confirmation is given, and — per the
  fix in `SKILL.md` Axis Re-Calibration (the "if the learner accepts" bullet)
  — the triggering streak resets to 0 so it doesn't immediately re-fire
  against the level Sage just applied.
- It also checks that a second, later streak crossing the same threshold is
  measured against the *new* `axis_overrides` level (medium, not low) — a
  genuinely fresh signal earning a genuinely fresh offer, worded for the new
  baseline.

## Setup
Scratch directory with `.sage-progress.json`:
```json
{
  "active_track": "python-basics",
  "tracks": {
    "python-basics": {
      "phase": 0,
      "completed_exercises": ["P0-fizzbuzz", "P0-temp-converter"],
      "current_topic": "Control flow",
      "current_exercise": "P0-word-counter",
      "next_up": "P1-list-ops",
      "observations": "",
      "topic_confidence": {},
      "review_due": [],
      "axis_overrides": {},
      "low_hint_streak": 2,
      "high_hint_streak": 0,
      "last_session": "",
      "hint_count": 0
    }
  }
}
```
(`low_hint_streak: 2` simulates `P0-fizzbuzz` and `P0-temp-converter` both
already completed with zero hints. Curriculum declares `mastery: low`.)
Valid `.sage-profile.md`.

## Script
1. Learner works `P0-word-counter` (Phase 0's last exercise) needing **zero**
   hints, submits a correct solution. Verify passes. `low_hint_streak` should
   become 3 — this IS the end of Phase 0, so the phase-transition
   AskUserQuestion fires.
2. At the phase-transition question, the recalibration option should be
   present (per the streak state) — check its exact wording ("the last few
   exercises... bump Mastery to medium?" or clearly equivalent).
3. Learner picks the **recalibration option**, i.e. accepts the bump.
4. Learner starts Phase 1, completes `P1-list-ops` with zero hints.
5. Learner completes `P1-comprehension-refactor` (Phase 1's second of three
   exercises) with zero hints. `low_hint_streak` reaches 2 here, but this is
   **not** a phase-transition point.
6. Learner completes `P1-json-roundtrip` (Phase 1's actual last exercise)
   with zero hints again, so the streak isn't broken by a hint-needed pass.
   This IS the end of Phase 1 → the phase-transition AskUserQuestion fires.
7. Learner accepts this second recalibration offer too.

## Assertions

- `[behavioral]` The recalibration option's wording at step 2 says "the last
  few exercises" (or clearly equivalent phrasing that doesn't scope to a
  single phase) and names bumping Mastery upward — quote it directly.
- `[mechanical]` After step 3 (accept), `axis_overrides.mastery == "medium"`
  in the progress file — diff before/after. `curricula/python-basics.md` on
  disk is unchanged (`mastery: low` still declared there; the override layers
  on top, it never overwrites the source file).
- `[behavioral]` At step 3, Sage confirms what changed in one sentence (per
  SKILL.md: "Confirm what changed in one sentence") — quote it.
- `[mechanical]` After step 3, `low_hint_streak` is reset to `0` in the
  progress file — the accept branch resets the triggering streak same as
  decline does, so it doesn't immediately resurface against the level just
  applied.
- `[behavioral]` After step 4 (first Phase 1 zero-hint exercise post-accept),
  no recalibration offer fires yet — the streak was reset in step 3, so this
  is only the first exercise of a new streak (`low_hint_streak == 1`), below
  threshold.
- `[behavioral]` After step 5, `low_hint_streak == 2` (still below the `>= 3`
  threshold) and, independent of that, `P1-comprehension-refactor` is not
  Phase 1's last exercise, so no phase-transition question fires at all here.
  Sage should show only the standard 4-option "Exercise complete. What
  next?" menu, with no 5th option.
- `[behavioral]` After step 6 (Phase 1's actual last exercise, phase
  transition fires), `low_hint_streak == 3` and a **fresh** recalibration
  offer is presented — confirm it's worded against the *new* baseline (e.g.
  "bump Mastery to high?", not a repeat of "bump Mastery to medium?" since
  `axis_overrides.mastery` is already `medium` at this point).
- `[mechanical]` After step 7 (second accept), `axis_overrides.mastery ==
  "high"` and `low_hint_streak` is reset to `0` again.
- `[mechanical]` `python3 tests/check_progress_schema.py <scratch-dir>` exits
  0 at every checkpoint.
