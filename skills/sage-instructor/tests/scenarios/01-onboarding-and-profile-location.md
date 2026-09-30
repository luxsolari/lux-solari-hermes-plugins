# Scenario 01 — Onboarding, existing-track offer, profile location

## Regression target
- Generated learner profiles must land at `.sage-profile.md` in the project
  root, never inside `skills/sage-instructor/references/` (fixed in 1.2.0 —
  the plugin directory can be wiped on reinstall). See `SKILL.md` "Load
  learner profile" and "Profile Setup."
- Track Setup Round 0 must offer the bundled `python-basics.md` curriculum by
  its `title` and skip straight to Phase 0 when picked — not fall through to
  the 4-round custom-track interview. See `SKILL.md` Round 0 and Track Setup.

## Setup
Empty scratch directory. No `.sage-profile.md`, no `.sage-progress.json`.
`skills/sage-instructor/curricula/` contains `TEMPLATE.md` and
`python-basics.md` (title: "Python Foundations") exactly as shipped in this
repo — don't modify them for this scenario.

## Script
1. Learner runs `/sage-start`.
2. Profile Setup, answer each round exactly:
   - Identity: "Ana, backend engineer"
   - Bridge languages: Python, Go
   - Experience: "Mid-level (3-5yr)"
   - Learning style: "Hands-on first"
   - Tone: "Direct and concise"
   Confirm the generated profile looks right.
3. Track Setup Round 0 should fire (no `active_track` yet, curricula/ has
   more than just TEMPLATE.md). Learner picks "Python Foundations" (the
   existing python-basics track), not "Build a custom track."
4. Learner runs `/sage-lesson`.

## Assertions

- `[mechanical]` `.sage-profile.md` exists at the scratch project root.
- `[mechanical]` No profile file was written under
  `skills/sage-instructor/references/` (that directory only ever contains
  `learner-profile-template.md`, unchanged).
- `[mechanical]` `python3 tests/check_progress_schema.py <scratch-dir>` exits
  0 on the resulting `.sage-progress.json`.
- `[behavioral]` Round 0 presented "Python Foundations" as a pickable option
  alongside "Build a custom track" — the learner was not forced through
  Round 1-4 of the custom-track interview.
- `[behavioral]` Picking the existing track set `active_track` to
  `python-basics` and jumped straight to Phase 0 content — no custom-track
  questions ("What do you want to learn?", destination project, etc.) were
  asked.
- `[behavioral]` The Step 1/2 lesson content actually referenced the
  learner's stated bridge languages (Python and/or Go) per the Bridge step,
  not a generic bridge language chosen without regard to the profile.
