# Scenario 08 — /sage-tracks and /sage-switch across two real tracks

## Regression target
- `/sage-tracks` and `/sage-switch` have only ever existed alongside a single
  real bundled curriculum (`python-basics`) — never exercised with a second
  one actually present, per issue #2's "out of scope for this pass" list.
  `SKILL.md`'s spec for `/switch` is a single line ("Save current, load
  new.") — thin enough that per-track isolation is only implicit in the
  progress file's `tracks: {}` shape (see Progress File Format), not spelled
  out as behavior.
- This scenario adds `rust-cli` (declared `mastery: medium, consequence:
  high, intent: output` — sharply different from `python-basics`'s `low,
  low, growth`) and checks three things `/switch` could plausibly get wrong:
  progress isolation (one track's state corrupting or leaking into the
  other's), axis calibration isolation (teaching posture bleeding from one
  track's declared axes into the other), and `/tracks` status accuracy
  across multiple real entries.

## Setup
Requires both `curricula/python-basics.md` and `curricula/rust-cli.md` to
exist. Scratch directory with `.sage-progress.json`:
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
      "topic_confidence": {"variables-dynamic-typing-truthiness": "solid"},
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
(No `rust-cli` entry yet — that track has never been started.) Valid
`.sage-profile.md`.

## Script
1. Learner runs `/sage-tracks`. Check the listing before touching anything.
2. Learner works `P0-temp-converter` (python-basics) needing zero hints,
   submits a correct solution. Verify passes. `low_hint_streak` becomes 2,
   `current_exercise` advances to `P0-word-counter`. This is deliberately
   *not* a phase transition (one exercise remains in Phase 0) — just
   building distinguishable state to check for corruption later.
3. Learner runs `/sage-switch rust-cli`.
4. Learner works `P0-word-count` (rust-cli's first exercise — note the
   different destination, `Ferrogrep`, and topics from Phase 0 of
   `curricula/rust-cli.md`) needing 3+ hints, submits a correct solution.
   Verify passes.
5. Learner runs `/sage-switch python-basics`.
6. Learner runs `/sage-tracks` again.

## Assertions

- `[behavioral]` At step 1, `/sage-tracks` lists both `python-basics`
  (status: started/active — it's `active_track` and has completed
  exercises) and `rust-cli` (status: not started — no entry in `tracks`
  yet), each showing the title and destination from its own YAML header
  (`Python Foundations`/Taskwright vs. `Rust CLI Tools`/Ferrogrep).
- `[mechanical]` After step 3 (switch), `.sage-progress.json` has
  `active_track == "rust-cli"`, a new `tracks.rust-cli` entry initialized at
  phase 0 with empty `completed_exercises`/`axis_overrides` and zeroed
  streaks, AND `tracks.python-basics` unchanged from its step-2 state
  (`current_exercise: "P0-word-counter"`, `low_hint_streak: 2`,
  `completed_exercises: ["P0-fizzbuzz", "P0-temp-converter"]`) — diff
  before/after the switch to confirm nothing in the other track's entry was
  touched.
- `[behavioral]` During step 4's lesson delivery, Sage's teaching posture
  reflects `rust-cli`'s own declared axes (`mastery: medium` → compressed
  concept+bridge per `references/philosophy.md`; `consequence: high` →
  explicit verification framing, no black-box treatment of the borrow
  checker's rejection; `intent: output` → efficient, compressed Steps 1-4) —
  not `python-basics`'s `low`/`low`/`growth` posture. Quote the specific
  transcript moment and cite the philosophy.md row it matches.
- `[mechanical]` After step 4, `tracks.rust-cli.high_hint_streak == 1` and,
  critically, `tracks.python-basics.high_hint_streak` is still `0` (or
  whatever it was before step 3) — a hint-heavy exercise on one track must
  not touch the other track's streaks.
- `[mechanical]` After step 5 (switch back), `active_track ==
  "python-basics"` and `tracks.python-basics` resumes exactly where step 2
  left it (`current_exercise: "P0-word-counter"`, `low_hint_streak: 2`,
  `completed_exercises` unchanged) — not reset, not re-onboarded from Phase
  0.
- `[behavioral]` At step 6, `/sage-tracks` now shows both tracks as started,
  with `python-basics` correctly marked active again (not `rust-cli`, which
  was only switched away from, not abandoned).
- `[mechanical]` `axis_overrides` is `{}` for both tracks at every
  checkpoint — this scenario never triggers a recalibration offer, so a
  non-empty override anywhere would mean something wrote to the wrong place.
- `[mechanical]` `python3 tests/check_progress_schema.py <scratch-dir>`
  exits 0 at every checkpoint, confirming the schema checker validates a
  multi-track file correctly (it loops over every key under `tracks`, not
  just `active_track`).
