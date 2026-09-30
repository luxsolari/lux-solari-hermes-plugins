# Scenario 09 — Grounding-research trigger branch (custom-track creation)

## Regression target

`SKILL.md`'s Track Setup gained a grounding-research step: before generating
a custom curriculum, Sage judges whether the topic is a fast-moving
library/framework with a versioned, changing API (vs. stable fundamentals
training data already gets right), and if so, uses WebSearch/WebFetch to
pull current docs before writing exercises — recording what it consulted in
the curriculum's `sources` field. Scenario 06 exercises this same custom-
track path with "Rust" (a *stable* topic — its 06 assertions confirm the
step correctly does **not** fire). This scenario exercises the *other*
branch: a topic that should trigger it — bridging into a real, versioned
game library — and checks that the research actually happened (a real tool
call, not a narrated one) and actually shaped the output, not just that a
`sources` field got stapled on for show.

## Setup

Empty scratch directory. No `.sage-profile.md`, no `.sage-progress.json`.
`skills/sage-instructor/curricula/` contains `TEMPLATE.md`, `python-basics.md`,
and `rust-cli.md` exactly as shipped — don't modify them for this scenario.
This run needs real WebSearch/WebFetch access; if unavailable in the
execution environment, stop and report that as an environment limitation
rather than narrating a plausible-looking search result. The trigger message
deliberately doesn't name a topic — this scenario's regression target is the
grounding-research step at generation time, not Round 0's trigger-already-
named-a-topic skip/compress behavior (see scenario 10 for that); the topic
is revealed at Round 1 instead, so Round 0 fires normally here.

## Script

1. Learner triggers Sage via natural language, with no topic stated yet: "I
   want to pick up something new for making small games on the side."
2. Profile Setup — answer each round exactly:
   - Identity: "Sam, web developer"
   - Bridge languages: JavaScript, TypeScript
   - Experience: "Junior (1-3yr)"
   - Learning style: "Hands-on first"
   - Tone: "Sardonic humor welcome"
   Confirm the generated profile looks right.
3. Track Setup Round 0 fires (curricula/ has more than TEMPLATE.md, and no
   topic was named yet). Learner picks **"Build a custom track"**.
4. Round 1 ("What do you want to learn?"): "C++, and Raylib to build small
   games."
5. Round 2 ("Is there a project this feeds into?"): Yes — "A couple small
   personal games, just for fun, nothing shipped or shared with anyone."
6. Round 3 ("How much do you know already?"): "Know a related language."
7. Round 4 ("What's the priority?"): "Build while learning (Balanced)."
8. Before generating, Sage judges Raylib warrants a grounding check (a
   versioned game library, not a language's stable core syntax) and actually
   issues a WebSearch/WebFetch call for current Raylib docs — execute this
   for real, don't narrate a plausible result.
9. Sage briefly tells the learner what it checked, then presents the
   generated curriculum for confirmation.
10. Learner confirms.
11. Learner runs `/sage-lesson`.

## Assertions

- `[mechanical]` A new file exists at `curricula/<slug>.md` with a YAML
  header containing every field `TEMPLATE.md` marks required: `track`,
  `title`, `destination`, `mastery`, `consequence`, `intent`, `bridge_from`,
  `teaches`, `verify`.
- `[mechanical]` The header's `sources` field **is present** and non-empty,
  containing at least one real, plausible Raylib-related URL (e.g. an actual
  raylib.com page) — the direct contrast to scenario 06's confirmed absence
  for a stable topic.
- `[mechanical]` `verify` is a real, non-placeholder command appropriate for
  compiling a C++/Raylib program (references an actual Raylib linking
  flag/library, e.g. `-lraylib` or an equivalent build invocation) — not
  `TEMPLATE.md`'s literal g++ example copied verbatim without adapting it
  for Raylib linkage.
- `[behavioral]` The transcript shows a real WebSearch/WebFetch tool call
  before the curriculum was generated, not a narrated/assumed result — quote
  the query and confirm the returned content is genuine Raylib
  documentation, not fabricated.
- `[behavioral]` Sage told the learner what it checked (a sentence
  referencing the research, per `SKILL.md`'s grounding-research step) before
  presenting the curriculum for confirmation — quote it.
- `[behavioral]` At least one specific Raylib API element named in the
  generated exercises/topics (a function, constant, or concept) matches real
  Raylib documentation rather than a plausible-sounding invention — name the
  element and confirm it against what the research step actually found.
- `[behavioral]` `consequence: low` in the generated header — Round 2
  described unshipped, unshared personal games, matching `SKILL.md`'s
  inference rule for a personal/learning-only project. Quote the header and
  the reasoning.
- `[behavioral]` `mastery` reflects Round 3's "Know a related language"
  answer and `intent: balanced` reflects Round 4 — quote the header and
  confirm both map from the interview, not defaulted.
- `[behavioral]` Sage displayed the generated curriculum and explicitly
  asked the learner to confirm **before** saving — quote the confirmation
  prompt. The file must not exist on disk before that confirmation turn
  (check between steps 9 and 10).
- `[mechanical]` `.sage-progress.json`'s `active_track` matches the new
  curriculum's `track` slug, and `python3 tests/check_progress_schema.py
  <scratch-dir>` exits 0.
