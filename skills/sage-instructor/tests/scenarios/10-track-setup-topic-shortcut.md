# Scenario 10 — Track Setup's topic-already-stated shortcut

## Regression target

`SKILL.md`'s Track Setup gained a rule: when the learner's trigger message
already names a specific topic (instead of a bare `/sage-start`), don't ask
Round 0 blind. If the topic clearly matches no existing curriculum, skip
Round 0's question entirely and go straight into the custom-track interview
— and skip Round 1 too, since "what do you want to learn?" was already
answered. If it clearly matches one, compress Round 0 into a direct confirm
naming that track, instead of the generic "want to start one of these"
list. Neither branch has ever been exercised — scenarios 06/09 deliberately
use a topic-neutral trigger so their own regression targets (custom-track
generation, grounding-research) aren't entangled with this. This scenario
covers both branches directly, in two independent parts.

## Setup

Two independent empty scratch directories (Part A, Part B), each with no
`.sage-profile.md`/`.sage-progress.json`. Both use
`skills/sage-instructor/curricula/` containing `TEMPLATE.md`,
`python-basics.md`, and `rust-cli.md` exactly as shipped — don't modify them.

## Part A — No match (skip Round 0 and Round 1 entirely)

### Script
1. Learner triggers Sage via natural language: "Teach me Elixir, I want to
   build something small." (No bundled curriculum teaches Elixir.)
2. Profile Setup — answer each round:
   - Identity: "Priya, backend engineer"
   - Bridge languages: Erlang, Python
   - Experience: "Intermediate"
   - Learning style: "Hands-on first"
   - Tone: "Direct and concise"
   Confirm the generated profile looks right.
3. Track Setup: per the new rule, Round 0's "want to start one of these, or
   build something custom?" question should NOT be asked — Elixir matches
   neither `python-basics` nor `rust-cli`. Sage should say so in one line
   and go straight into the custom-track interview.
4. Round 1 should also be skipped — the topic was already stated in step 1.
   Sage proceeds directly to Round 2 ("Is there a project this feeds
   into?"): Yes — "A small message queue consumer for a personal project."
5. Round 3 ("How much do you know already?"): "Basics but rusty."
6. Round 4 ("What's the priority?"): "Pure learning (Growth)."
7. Sage generates the curriculum and presents it for confirmation.
8. Learner confirms.

### Assertions
- `[behavioral]` Round 0's "want to start one of these, or build something
  custom?" question (or the generic per-curriculum option list) was never
  presented — quote the transcript showing the trigger message led directly
  to a one-line acknowledgment plus the custom-track interview, not a
  separate Round 0 turn.
- `[behavioral]` That acknowledgment explicitly said no bundled track covers
  the stated topic (Elixir) — quote it.
- `[behavioral]` Round 1's "What do you want to learn?" was never separately
  asked — the transcript goes from the acknowledgment straight to Round 2's
  question, carrying "Elixir" forward as the already-given answer.
- `[mechanical]` The generated curriculum's `teaches` field names Elixir
  (the topic actually stated in step 1) — not a mismatched or re-derived
  topic, proving the carried-forward answer was used, not re-solicited and
  potentially drifted.
- `[mechanical]` `.sage-progress.json`'s `active_track` matches the new
  curriculum's `track` slug, and `python3 tests/check_progress_schema.py
  <scratch-dir-A>` exits 0.

## Part B — Clear match (compress Round 0, don't skip it)

### Script
1. Learner triggers Sage via natural language: "Teach me Python, I want to
   build something with it." (Matches `python-basics`'s `teaches`/`title`.)
2. Profile Setup — answer each round:
   - Identity: "Devon, QA engineer"
   - Bridge languages: JavaScript
   - Experience: "Junior (1-3yr)"
   - Learning style: "Read first, then try"
   - Tone: "Encouraging and patient"
   Confirm the generated profile looks right.
3. Track Setup: per the new rule, Round 0 should still be asked (this is a
   real choice — bundled structured track vs. one generated fresh) but
   compressed into a direct confirm naming the match, e.g. "Sounds like
   Python — want the bundled Python Foundations track, or build a custom
   one instead?" — not the full undifferentiated list including Rust CLI
   Tools. Learner picks **"build a custom one instead"** — explicitly
   declining the matched bundled track, to prove the compression didn't
   remove the choice.
4. Round 1 should be skipped (Python was already stated) — Sage proceeds
   directly to Round 2 ("Is there a project this feeds into?"): No —
   general skill building.
5. Round 3 ("How much do you know already?"): "Intermediate."
6. Round 4 ("What's the priority?"): "Get productive fast (Output)."
7. Sage generates the curriculum and presents it for confirmation.
8. Learner confirms.

### Assertions
- `[behavioral]` Round 0's question referenced the matched track by name
  (Python / "Python Foundations") rather than presenting the generic
  "want to start one of these" list with every bundled curriculum —
  quote it.
- `[behavioral]` The compressed question still offered the custom-track
  alternative explicitly (didn't railroad toward the bundled match) —
  quote the option.
- `[behavioral]` Picking custom despite the matched offer correctly
  proceeded into the custom-track interview (not silently defaulted to
  `active_track: python-basics`) — confirm `active_track` in the final
  progress file is a new custom slug, not `python-basics`.
- `[behavioral]` Round 1's "What do you want to learn?" was never separately
  asked — the transcript goes from Round 0's confirm straight to Round 2,
  carrying "Python" forward.
- `[mechanical]` `.sage-progress.json`'s `active_track` matches the new
  custom curriculum's `track` slug (not `python-basics`), and `python3
  tests/check_progress_schema.py <scratch-dir-B>` exits 0.
