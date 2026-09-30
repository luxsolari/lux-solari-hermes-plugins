# Curriculum Template

Use this file as a blueprint when creating a new learning track. Copy it, rename it to `your-track-name.md`, fill in the sections, and drop it in the `curricula/` folder.

Sage reads the YAML header to understand the track's context and calibration. The phases, topics, and exercises form the actual course content.

---

## YAML Header (required)

Every curriculum MUST start with this header. Sage uses it to calibrate teaching.

```yaml
---
track: your-track-name          # Lowercase, hyphenated. Used in progress file and /switch command.
title: "Human-Readable Title"   # Displayed in /tracks and /progress.
destination: "Project Name"     # The real project this track feeds into. Can be "general" if none.
description: >
  One or two sentences about what this track covers and why.

# Three Axes calibration (from DEV_PHILOSOPHY)
mastery: low                    # low | medium | high — learner's current level in this domain
consequence: low                # low | medium | high — what breaks if something goes wrong
intent: growth                  # growth | balanced | output — what's the priority

# Bridge languages — Sage will connect new concepts to these
bridge_from:
  - Java
  - Python

# Prerequisites — what should the learner know before starting
prerequisites:
  - "Basic programming (variables, loops, functions)"
  - "OOP fundamentals"

# Language/tools this track teaches
teaches:
  - C++
  - Raylib
  - CMake

# Optional — real-world references Sage consulted while generating this
# curriculum (Track Setup's grounding-research step). Only present when that
# step ran; omit entirely for tracks generated from stable, well-known
# fundamentals that didn't need a live check. Title + URL is enough.
sources:
  - "Raylib cheatsheet — https://www.raylib.com/cheatsheet/cheatsheet.html"

# How Sage verifies an exercise before marking it complete (Step 6b).
# Either a shell command template — {file} is substituted with the exercise's
# entry point — or the literal string "manual" for exercises with no
# meaningful automated check (design docs, architecture exercises, etc.).
verify: "g++ -std=c++17 {file} -o /tmp/sage_out && /tmp/sage_out"
---
```

---

## Phase Structure

Organize the track into numbered phases. Each phase should have:

### Required Elements
- **Goal:** One sentence — what the learner can do after this phase.
- **Pace:** How fast to move (fast/medium/slow) and why.
- **Topics:** What concepts are covered.
- **Exercises:** Checkboxed list. Each exercise has a name in `PHASENUMBER-slug` format.
- **[Destination] Connection:** How this phase connects to the destination project.

### Phase Template

```markdown
## Phase N: [Phase Title]
**Goal:** [What the learner can do after completing this phase.]
**Pace:** [Fast/Medium/Slow] — [why this pace]

### Topics
- Topic 1
- Topic 2
- Topic 3

### Exercises
- [ ] `PN-exercise-slug` — [Brief description of what to build/do]
- [ ] `PN-another-exercise` — [Brief description]

### [Destination Project] Connection
[How this phase's skills apply to the destination project. Make it concrete.]
```

---

## Exercise Naming Convention

Exercises are tracked by name in the progress file. Use this format:

```
P{phase_number}-{descriptive-slug}
```

Examples:
- `P0-hello-world`
- `P1-dynamic-array`
- `P3-event-system`
- `P5-state-machine`

Keep slugs short, lowercase, hyphenated, and descriptive enough to recognize at a glance in a progress report.

---

## Tips for Good Curricula

1. **Each phase should end with a working thing.** Not partial progress — something that compiles/runs and demonstrates the concept.

2. **3-5 exercises per phase is the sweet spot.** Fewer than 3 doesn't give enough practice. More than 5 makes a phase feel endless.

3. **Scale difficulty within each phase.** First exercise is gentle, last exercise stretches. Across phases, difficulty compounds.

4. **Connect every phase to the destination.** If the learner can't see why this matters for their project, motivation drops. The connection paragraph isn't optional.

5. **Name the traps.** If there are common misconceptions or tricky parts, call them out in the topics. Sage uses these to preempt confusion.

6. **Include cross-cutting concerns.** Things like debugging, testing, version control — thread them throughout, don't make them a separate phase.

7. **Make `verify` actually runnable — and prefer the more portable binary name.** If it needs a compiler flag or interpreter that isn't on every machine, say so in `prerequisites`. A `verify` command that fails on a correct solution is worse than no verification at all. Concrete trap: on Windows, `python3` often resolves to a Microsoft Store App Execution Alias stub that prints an install prompt and exits non-zero instead of running anything — `python` is the safer default there. Sage's Step 6b will try to catch this class of failure and flag it as a toolchain issue rather than a learner bug, but a `verify` command that just works avoids the ambiguity entirely.

---

## Example: Minimal Two-Phase Curriculum

```markdown
---
track: python-basics
title: "Python Foundations"
destination: "Numbercaster"
description: >
  Core Python fluency from syntax through OOP, building toward
  the Numbercaster AI wizard project.
mastery: low
consequence: low
intent: growth
bridge_from:
  - Java
prerequisites:
  - "Programming fundamentals in any language"
teaches:
  - Python
verify: "python {file}"
---

## Phase 0: Syntax & Flow
**Goal:** Write basic Python scripts confidently.
**Pace:** Fast — these concepts transfer from Java.

### Topics
- Variables, types, dynamic typing
- Control flow (if/elif/else, for, while)
- Functions, default args, *args/**kwargs
- List comprehensions

### Exercises
- [ ] `P0-fizzbuzz` — Classic FizzBuzz in Python
- [ ] `P0-list-ops` — Build a contact list with add/search/delete using lists and dicts

### Numbercaster Connection
After this phase, you can write the basic game loop and input handling.

---

## Phase 1: Data Structures & OOP
**Goal:** Use Python's built-in structures and write clean classes.
**Pace:** Medium — OOP maps from Java but Pythonic idioms differ.

### Topics
- Dicts, sets, tuples — when to use which
- Classes, __init__, __str__, __repr__
- Inheritance vs composition in Python
- Properties and descriptors

### Exercises
- [ ] `P1-card-classes` — Model a deck of cards with classes
- [ ] `P1-game-state` — Build a GameState class that tracks player progress
- [ ] `P1-pythonic-refactor` — Refactor P0 exercises to use Pythonic idioms

### Numbercaster Connection
The card and game state classes are direct building blocks for Numbercaster's core.
```

---

*Use this template. Adapt it. Make it yours. Every track Sage teaches gets better because the structure is consistent.*
