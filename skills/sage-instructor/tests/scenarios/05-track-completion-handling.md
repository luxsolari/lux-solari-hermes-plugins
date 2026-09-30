# Scenario 05 — Completing a track's actual last exercise

## Regression target
When the exercise just completed is the curriculum's actual last exercise,
there's nothing left to promote to `current_exercise`/`next_up`. `SKILL.md`
Step 6b point 8 requires: set `next_up` to `null`, treat this as track
completion, congratulate the learner concretely on what the whole track
unlocked, and offer `/tracks` or `/new-track` instead of the standard
"Exercise complete. What next?" four-option prompt.

## Setup
Scratch directory with `.sage-progress.json`:
```json
{
  "active_track": "python-basics",
  "tracks": {
    "python-basics": {
      "phase": 2,
      "completed_exercises": [
        "P0-fizzbuzz", "P0-temp-converter", "P0-word-counter",
        "P1-list-ops", "P1-comprehension-refactor", "P1-json-roundtrip",
        "P2-task-class", "P2-task-list"
      ],
      "current_topic": "Combining classes with json persistence",
      "current_exercise": "P2-persistent-tasklist",
      "next_up": null,
      "observations": "Strong OOP fundamentals, fast through Phase 2.",
      "topic_confidence": {"classes": "solid"},
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
(`P2-persistent-tasklist` is `python-basics.md`'s actual final exercise —
`next_up` is already `null` because nothing follows it.)
Valid `.sage-profile.md`.

## Script
1. Learner works `P2-persistent-tasklist` — a `TaskList` extended to
   save/load itself via JSON, per the curriculum's exercise description.
   Submit a genuinely correct solution so `verify` (`python {file}`) passes
   cleanly; the point of this scenario is the completion-handling branch, not
   the failure path.
2. Observe what Sage does immediately after the passing verify run.

## Assertions

- `[mechanical]` `P2-persistent-tasklist` is added to `completed_exercises`.
- `[mechanical]` `next_up` remains `null` and `current_exercise` is NOT
  advanced to some invented exercise name — there is nothing after this one
  in the curriculum.
- `[behavioral]` Sage did NOT present the standard "Exercise complete. What
  next?" AskUserQuestion with its four usual options (save/refactor/review/
  bonus challenge).
- `[behavioral]` Sage congratulated the learner concretely on what the whole
  track unlocked — referencing the actual destination project (Taskwright)
  and specifically what these exercises built toward it (e.g. `Task`/
  `TaskList` classes plus JSON persistence being Taskwright's domain model
  and persistence layer), not a generic "great job, track complete."
- `[behavioral]` Sage then offered `/tracks` (start another existing track)
  or `/new-track` (build a custom one) as the next step.
- `[mechanical]` `python3 tests/check_progress_schema.py <scratch-dir>` exits
  0 on the final state (the `next_up: null` check should surface as a WARN
  telling the grader to confirm this manually, not a FAIL).
