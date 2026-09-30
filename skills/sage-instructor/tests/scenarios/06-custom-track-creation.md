# Scenario 06 — Custom-track creation (Track Setup Rounds 1-4)

## Regression target

Every prior scenario (01-05) and the 1.2.1 real-install smoke test picked the
**existing** bundled track at Track Setup Round 0. The custom-track path —
Round 0's "Build a custom track" branch, the four-round interview, curriculum
generation from `TEMPLATE.md`, confirm-before-save, and the resulting
curriculum actually landing in `curricula/<track>.md` — is fully specified in
`SKILL.md` (Track Setup, Rounds 1-4) but has never been exercised end-to-end.
This is the last major untested path from a fresh install.

## Setup

Empty scratch directory. No `.sage-profile.md`, no `.sage-progress.json`.
`skills/sage-instructor/curricula/` contains `TEMPLATE.md`, `python-basics.md`,
and `rust-cli.md` exactly as shipped — don't modify them for this scenario.
The learner's trigger message deliberately doesn't name a topic — this
scenario is testing Round 0's normal, un-tuned behavior (the full option
list), not the trigger-already-named-a-topic skip/compress path (see
scenario 10 for that). The topic (Go, which has no bundled equivalent among
these three files) is only revealed at Round 1.

## Script

1. Learner triggers Sage via natural language (not a slash command), with no
   topic stated yet: "Hey, I want to pick up a new skill — what have you
   got?"
2. Profile Setup — answer each round:
   - Identity: "Marco, mobile developer"
   - Bridge languages: Java, Kotlin
   - Experience: "Junior (1-3yr)"
   - Learning style: "Hands-on first"
   - Tone: "Encouraging and patient"
   Confirm the generated profile looks right.
3. Track Setup Round 0 fires (curricula/ has `python-basics.md` and
   `rust-cli.md` beyond just `TEMPLATE.md`, no `active_track` yet, and no
   topic was named yet — nothing to compress or skip). Learner explicitly
   picks **"Build a custom track"** — not "Python Foundations" or "Rust CLI
   Tools."
4. Round 1 ("What do you want to learn?"): "Go."
5. Round 2 ("Is there a project this feeds into?"): Yes — "A small CLI tool
   that recursively greps through a directory, like a mini ripgrep clone."
6. Round 3 ("How much do you know already?"): "From scratch."
7. Round 4 ("What's the priority?"): "Build while learning (Balanced)."
8. Sage generates the curriculum and presents it for confirmation before
   saving.
9. Learner confirms.
10. Learner runs `/sage-lesson`.

## Assertions

- `[mechanical]` A new file exists at `curricula/<slug>.md` (some
  Go-related track slug) with a YAML header containing every field
  `TEMPLATE.md` marks required: `track`, `title`, `destination`, `mastery`,
  `consequence`, `intent`, `bridge_from`, `teaches`, `verify`.
- `[mechanical]` `verify` is a real, non-placeholder command appropriate for
  Go (e.g. involving `go run` or `go build`) — not `TEMPLATE.md`'s literal
  C++/g++ example copied verbatim, and not empty/missing.
- `[mechanical]` `.sage-progress.json`'s `active_track` matches the new
  curriculum's `track` slug, and `python3 tests/check_progress_schema.py
  <scratch-dir>` exits 0.
- `[behavioral]` `mastery: low` (from Round 3's "From scratch") and
  `intent: balanced` (from Round 4's "Build while learning (Balanced)") —
  quote the generated YAML header and confirm both map correctly from the
  interview answers, not defaulted or guessed independently of them.
- `[behavioral]` `destination` reflects Round 2's actual stated project (the
  CLI grep tool), not `"general"` or a generic placeholder — Round 2 was
  answered "Yes" with a specific project named.
- `[behavioral]` `bridge_from` reflects the learner's real profile languages
  (Java and/or Kotlin from Profile Setup) — not invented languages the
  learner never stated.
- `[behavioral]` Sage displayed the generated curriculum (at least its
  structure/header) and explicitly asked the learner to confirm **before**
  saving it — quote the confirmation prompt. The file must not exist on disk
  before that confirmation turn (check between steps 8 and 9).
- `[mechanical]` Round 0 offered all three real options — "Python
  Foundations", "Rust CLI Tools", and "Build a custom track." (per `SKILL.md`
  line 89, one per existing curriculum plus custom) — and the learner picked
  custom (same mechanism scenario 01 already proved works for an existing-
  track pick — this exercises the custom branch instead).
- `[mechanical]` The generated YAML header has **no** `sources` field. "Go"
  (the language, its core syntax/tooling) is stable-fundamentals territory
  per `SKILL.md`'s grounding-research rule — training data doesn't need a
  live check for this, so the field should be entirely absent, not
  present-but-empty. (Contrast: scenario 09 exercises a topic where the field
  *should* appear.)
