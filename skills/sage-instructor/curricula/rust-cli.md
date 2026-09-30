---
track: rust-cli
title: "Rust CLI Tools"
destination: "Ferrogrep — a production Rust CLI search tool the team relies on"
description: >
  Rust fluency from ownership through idiomatic error handling and
  iterator-based collection processing, building toward Ferrogrep, a
  real grep-style command-line search tool that ships to the rest of
  the team.

# Three Axes calibration (from DEV_PHILOSOPHY)
mastery: medium                 # low | medium | high — learner's current level in this domain
consequence: high                # low | medium | high — what breaks if something goes wrong
intent: output                  # growth | balanced | output — what's the priority

# Bridge languages — Sage will connect new concepts to these
bridge_from:
  - Python
  - Java
  - JavaScript/TypeScript

# Prerequisites — what should the learner know before starting
prerequisites:
  - "Programming fundamentals in any language (variables, control flow, functions)"
  - "Command-line comfort — running a compiled binary, reading a stack trace/panic"
  - "Rust toolchain installed (rustc on PATH)"

# Language/tools this track teaches
teaches:
  - Rust

# Every exercise is a standalone .rs file compiled and run directly —
# a clean exit (0) means the asserts passed. No cargo project scaffolding
# needed until Phase 2.
verify: "rustc --edition 2021 {file} -o /tmp/sage_out && /tmp/sage_out"
---

## Phase 0: Ownership & Core Syntax
**Goal:** Read and write basic Rust confidently — variables, control flow, and
enough ownership/borrowing to stop fighting the compiler on straightforward code.
**Pace:** Medium — control flow and functions transfer almost directly from
Python/Java; ownership and `Result`/`Option` instead of exceptions are the
genuinely new mental models, so don't compress those two.

### Topics
- Variables, mutability (`let` vs `let mut`), no implicit nulls
- Ownership and borrowing — move semantics, `&`/`&mut` references, why the
  borrow checker rejects code that looks fine in a GC language
- `Result<T, E>` / `Option<T>` and the `?` operator — no exceptions
- Pattern matching: `match`, `if let`
- `&str` vs `String` — borrowed vs owned text, the trap that bites first

### Exercises
- [ ] `P0-word-count` — Given a string, return a `HashMap<String, u32>` of word→count, printed in sorted order. Asserts against a known sentence.
- [ ] `P0-file-reader` — Read a file's contents via `std::fs::read_to_string`, propagating errors with `?` instead of `.unwrap()`. Asserts cover both an existing file and a missing one (the missing case must return `Err`, not panic).
- [ ] `P0-arg-parser` — Parse `std::env::args()` by hand (no crate) into a struct with a pattern and optional flags. Asserts against several fixed argument-vector inputs, including a malformed one that must produce a clear error.

### Ferrogrep Connection
This phase is Ferrogrep's skeleton: reading input safely (no panics on bad input) and parsing the flags the real tool will accept.

---

## Phase 1: Collections, Iterators & Errors
**Goal:** Use Rust's iterator combinators and a real custom error type
idiomatically, instead of manual loops and `.unwrap()`.
**Pace:** Medium — `Vec`/`HashMap` map from Python's list/dict, but chained
iterator adapters (`map`/`filter`/`collect`) and structured errors are new
idiom, not new concepts; compress the "why collections exist" part.

### Topics
- `Vec`, `HashMap`, `HashSet` — when to use which
- Iterator adapters: `map`, `filter`, `collect`, `enumerate`
- Custom error types: an `enum` implementing `std::error::Error`, `From` for `?`-based conversion
- Why "no black boxes in critical paths" means no swallowed errors here — every fallible path returns `Result`, never a silent default

### Exercises
- [ ] `P1-line-filter` — Filter a file's lines by substring using iterator combinators (no manual `for` loop), returning `Result<Vec<String>, Error>`.
- [ ] `P1-custom-error` — Define an `Error` enum (`Io`, `Pattern`, ...) and wire `?` to convert from `std::io::Error` via `impl From<std::io::Error> for Error`. Asserts confirm both variants are reachable and the conversion compiles without `.unwrap()`.
- [ ] `P1-pattern-match` — Implement a small literal-plus-`*`-wildcard matcher as a pure function (`fn matches(pattern: &str, line: &str) -> bool`), with asserts covering exact match, wildcard match, and non-match. This is Ferrogrep's matching engine in miniature.

### Ferrogrep Connection
`P1-pattern-match` and `P1-custom-error` become the tool's actual matching logic and error backbone — not a simplified stand-in, the real thing.

---

## Phase 2: Assembling the CLI
**Goal:** Wire Phase 0/1 into a real installable binary with correct exit
codes and no undefined failure states — the bar `consequence: high` demands
for something the team runs.
**Pace:** Fast — this phase is mostly composition of already-understood
pieces, so lean toward output mode: less new-concept teaching, more review
of the wiring and the exit-code contract.

### Topics
- `fn main() -> Result<(), Error>` and the process exit-code contract: grep semantics are `0` = match found, `1` = no match, `2` = error — three distinct outcomes, never conflated
- Reading from a file path vs. stdin
- Splitting a single-file prototype into modules (`mod args; mod search; mod error;`)
- Why "working" at this consequence level means correctly exiting on every path, not just the happy path — an exercise here isn't complete on a green compile alone

### Exercises
- [ ] `P2-search-core` — Wire `P0-arg-parser`, `P1-pattern-match`, and `P1-custom-error` into a `search(pattern: &str, path: &str) -> Result<Vec<String>, Error>` core function doing real file I/O. Asserts against a fixture file with known matching and non-matching lines.
- [ ] `P2-cli-wiring` — Build `main()` that parses real CLI args, calls `search`, prints matches, and returns the correct exit code for each of the three outcomes (match / no-match / error) — verified by actually running the compiled binary with different inputs and checking `$?`/exit status, not just reading the code.
- [ ] `P2-module-split` — Split the single-file prototype into `args.rs`, `search.rs`, `error.rs` modules compiled together. Asserts confirm the split binary behaves identically to the single-file version on the same fixture inputs.

### Ferrogrep Connection
After this phase, Ferrogrep is a real CLI the team can install and run — not a toy that only works when called exactly as demonstrated.
