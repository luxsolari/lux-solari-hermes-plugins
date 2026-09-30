# Scenario 02 — Topic-key derivation and reuse (Rule 10)

## Regression target
`topic_confidence`/`review_due` keys must be derived once per curriculum
Topics bullet (kebab-case, first-named concept for unlabeled/comma-separated
bullets) and reused verbatim everywhere after — not re-derived each time the
topic comes up. See `SKILL.md` Progress Rule 10.

The target bullet is `python-basics.md` Phase 0's first Topics entry:
`Variables, dynamic typing, truthiness` — unlabeled and comma-separated, so
Rule 10 says the key must be `variables` (the first-named concept), not
`dynamic-typing`, `truthiness`, or a compound of all three.

## Setup
Scratch directory with `.sage-progress.json`:
```json
{
  "active_track": "python-basics",
  "tracks": {
    "python-basics": {
      "phase": 0,
      "completed_exercises": [],
      "current_topic": "Variables, dynamic typing, truthiness",
      "current_exercise": "P0-fizzbuzz",
      "next_up": "P0-temp-converter",
      "observations": "",
      "topic_confidence": {},
      "review_due": [],
      "axis_overrides": {},
      "low_hint_streak": 0,
      "high_hint_streak": 0,
      "last_session": "",
      "hint_count": 0
    }
  }
}
```
and a `.sage-profile.md` (any valid profile — bridge language Java, mid-level,
hands-on).

## Script
1. Learner runs `/sage-lesson` (no topic given — picks up "Variables, dynamic
   typing, truthiness," the current topic).
2. At Step 5 (Comprehension Check), learner answers the first question
   **incorrectly** (deliberately pick a plausible-but-wrong option about
   truthiness, e.g. treating `0` or `""` as truthy). Sage revisits per Step 5;
   learner then answers **correctly**.
3. Learner completes `P0-fizzbuzz` with a correct solution; verify passes.
4. Learner runs `/sage-drill`.
5. Drill should pull from `review_due` first. Learner answers the
   drill question on this same topic **correctly**.

## Assertions

- `[mechanical]` After step 2, `topic_confidence` has exactly one new key,
  it is kebab-case, and its value is `"variables"` — not `"dynamic-typing"`,
  `"truthiness"`, or any multi-concept compound.
- `[mechanical]` `python3 tests/check_progress_schema.py <scratch-dir>` exits
  0 at every checkpoint (after step 2, after step 4).
- `[behavioral]` After step 2 (wrong-then-right), `topic_confidence["variables"]
  == "shaky"` and `"variables"` was added to `review_due` (Step 5 outcome
  rule: wrong-then-correct-after-revisit → `shaky`).
- `[behavioral]` The key used in step 5's drill round for this topic is
  **byte-for-byte identical** to the key set in step 2 — quote both
  occurrences from the transcript/file and confirm they match. This is the
  actual regression: a spec that re-derives the key at drill time instead of
  reusing the established one.
- `[behavioral]` After the correct drill answer in step 5, `"variables"` is
  removed from `review_due` and `topic_confidence["variables"] == "solid"`
  (drill-mode outcome rule).
