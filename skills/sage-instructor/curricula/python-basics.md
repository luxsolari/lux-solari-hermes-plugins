---
track: python-basics
title: "Python Foundations"
destination: "Taskwright — a CLI task tracker with persistent storage"
description: >
  Core Python fluency from syntax through OOP and file persistence,
  building toward Taskwright, a small command-line task tracker that
  saves state to disk between runs.

# Three Axes calibration (from DEV_PHILOSOPHY)
mastery: low                    # low | medium | high — learner's current level in this domain
consequence: low                # low | medium | high — what breaks if something goes wrong
intent: growth                  # growth | balanced | output — what's the priority

# Bridge languages — Sage will connect new concepts to these
bridge_from:
  - Java
  - JavaScript/TypeScript

# Prerequisites — what should the learner know before starting
prerequisites:
  - "Programming fundamentals in any language (variables, loops, functions)"
  - "Python 3 installed and on PATH"

# Language/tools this track teaches
teaches:
  - Python

# Every exercise is a standalone script with self-checking asserts —
# a clean exit (0) means the asserts passed.
verify: "python {file}"
---

## Phase 0: Syntax & Flow
**Goal:** Write basic Python scripts confidently — variables, control flow, functions.
**Pace:** Fast — these concepts transfer almost directly from Java/JS, the interesting part is the *shape* Python wants them in (indentation-as-blocks, dynamic typing, no `var`/`let`).

### Topics
- Variables, dynamic typing, truthiness
- Control flow: `if`/`elif`/`else`, `for` (over iterables, not indices), `while`
- Functions: default args, `*args`/`**kwargs`, no function overloading
- f-strings

### Exercises
- [ ] `P0-fizzbuzz` — Classic FizzBuzz 1-100. Self-check with asserts against a few known values (15 → "FizzBuzz", 7 → "7").
- [ ] `P0-temp-converter` — A function converting Celsius↔Fahrenheit, called both directions, with asserts pinning known conversion pairs.
- [ ] `P0-word-counter` — Given a string, return a dict of word→count. Asserts against a known sentence.

### Taskwright Connection
Phase 0 gets you the raw material for Taskwright's input loop — reading a command, branching on it, formatting output with f-strings.

---

## Phase 1: Data Structures & Functions
**Goal:** Choose the right built-in structure and write functions that operate on collections idiomatically.
**Pace:** Medium — dicts/lists map cleanly from Java's Map/List, but Python idioms (comprehensions, unpacking, `in`) are new muscle memory.

### Topics
- Lists, dicts, sets, tuples — when to use which
- List/dict comprehensions
- Unpacking, `enumerate`, `zip`
- Reading/writing JSON (`json` module)

### Exercises
- [ ] `P1-list-ops` — A contact list backed by a list of dicts: add, search by name, delete. Asserts covering all three operations.
- [ ] `P1-comprehension-refactor` — Take 3 loop-based transforms from Phase 0 and rewrite them as comprehensions. Asserts confirm identical output to the loop versions.
- [ ] `P1-json-roundtrip` — Serialize a list of dicts to a JSON file, read it back, assert the round-tripped data equals the original.

### Taskwright Connection
`P1-json-roundtrip` *is* Taskwright's persistence layer in miniature — saving tasks to disk and loading them back on the next run is exactly this pattern.

---

## Phase 2: OOP & Persistence
**Goal:** Model a small domain with classes and wire it to file-backed storage.
**Pace:** Medium — Python OOP maps from Java conceptually, but no access modifiers, `__init__` instead of constructors, and duck typing change the idiom.

### Topics
- Classes, `__init__`, `__repr__`/`__str__`
- Composition over inheritance (Python favors it)
- Properties for computed/validated attributes
- Combining classes with the `json` persistence from Phase 1

### Exercises
- [ ] `P2-task-class` — A `Task` class (title, done, priority) with `__repr__` and a `toggle_done()` method. Asserts on construction, toggling, and repr format.
- [ ] `P2-task-list` — A `TaskList` class composing multiple `Task`s: add, complete, list-pending. Asserts covering each method.
- [ ] `P2-persistent-tasklist` — Extend `TaskList` to save/load itself via JSON (reusing `P1-json-roundtrip`'s pattern). Assert that a saved-then-loaded `TaskList` matches the original.

### Taskwright Connection
This phase *is* Taskwright's core — `Task` and `TaskList` from these exercises become the actual domain model. What's left after Phase 2 is wiring a command-line input loop (Phase 0's branching) around them.
