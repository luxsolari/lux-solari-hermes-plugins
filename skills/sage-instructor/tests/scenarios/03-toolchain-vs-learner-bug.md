# Scenario 03 — Toolchain failure must not count as a learner bug

## Regression target
A `verify` run that fails for a reason that isn't a language-level
error/traceback from the learner's own code (missing interpreter, alias-stub
prompt, PATH issue, permissions error) must be recognized as a toolchain
problem, not counted against hint streaks, and not treated as a live Gotcha
requiring a code fix. See `SKILL.md` Step 6b point 3. This generalizes the
concrete `python3` Windows-alias-stub bug that shipped in `python-basics.md`
in 1.1.0 and was fixed in 1.2.0 — this scenario tests the general rule, not
just that one platform quirk.

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
      "topic_confidence": {"variables": "solid"},
      "review_due": [],
      "axis_overrides": {},
      "low_hint_streak": 1,
      "high_hint_streak": 0,
      "last_session": "",
      "hint_count": 0
    }
  }
}
```
and a valid `.sage-profile.md`.

## Script
1. Learner writes a genuinely correct `P0-temp-converter` solution
   (Celsius↔Fahrenheit conversion function with self-check asserts, per the
   curriculum's exercise description) and says they're done.
2. Before running the curriculum's real `verify` command, deliberately run
   the verify step against a **fabricated, guaranteed-missing interpreter
   name** instead — e.g. substitute the command with
   `sage_test_nonexistent_interpreter_xyz {file}` — so it fails with a shell
   "command not found" (exit 127), which is not a Python traceback and not a
   language-level error from the learner's code. Run this for real via Bash;
   don't narrate a plausible result.
3. Observe how Sage responds to that failure per Step 6b point 3.
4. Now run the *actual* curriculum `verify` command (`python {file}`) against
   the same correct solution. It should pass.

## Assertions

- `[behavioral]` In response to step 2's failure, Sage explicitly identified
  it as a toolchain/environment problem rather than a comprehension gap —
  quote the specific reasoning (e.g. noting the error isn't a Python
  traceback, or is a shell-level "not found").
- `[behavioral]` Sage did NOT treat the step 2 failure as a live Gotcha
  requiring the learner to fix their code, and did not ask a Socratic
  "what do you think went wrong with your code" question about it.
- `[behavioral]` Sage suggested a plausible toolchain-level fix (check
  interpreter name, check PATH) rather than silently retrying or blaming the
  solution.
- `[mechanical]` `hint_count`, `low_hint_streak`, and `high_hint_streak` were
  unchanged by step 2's failure — diff the progress file before/after step 2
  and confirm no streak fields moved.
- `[mechanical]` After step 4's real, passing verify run: `P0-temp-converter`
  is in `completed_exercises`, `low_hint_streak == 2` (this exercise added 0
  hints on top of the setup's existing streak of 1), `high_hint_streak == 0`,
  and `current_exercise`/`next_up` promoted per Step 6b point 8
  (`current_exercise` becomes `P0-word-counter`).
- `[mechanical]` `python3 tests/check_progress_schema.py <scratch-dir>` exits
  0 on the final state.
