#!/usr/bin/env python3
"""Deterministic structural checker for Sage's runtime artifacts.

Validates a .sage-progress.json (and optionally a sibling .sage-profile.md)
against the rules stated in skills/sage-instructor/SKILL.md's "Progress File
Format" / "Progress Rules" section. This catches spec-drift and schema
regressions mechanically -- it does NOT judge whether Sage's pedagogy was
good, only whether the artifacts it produced are well-formed. Pair with the
scenario transcripts in tests/scenarios/ for the behavioral checks.

Usage:
    python3 tests/check_progress_schema.py <project-dir>

Exit code 0 if every check passes, 1 otherwise. Findings are printed as
PASS/FAIL/WARN lines so a grading agent (or a human) can read the report
without re-deriving the rules.
"""
import json
import os
import re
import sys

KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SLUG = re.compile(r"^P\d+-[a-z0-9]+(-[a-z0-9]+)*$")
CONFIDENCE_LEVELS = {"solid", "shaky", "struggling"}
AXIS_KEYS = {"mastery", "consequence", "intent"}

results = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results.append((status, label, detail))
    return condition


def warn(label, condition, detail=""):
    status = "PASS" if condition else "WARN"
    results.append((status, label, detail))
    return condition


def note(label, detail=""):
    """Unconditional advisory -- always surfaces as NOTE with its detail
    visible, for things the script can observe but not itself verify
    (e.g. 'this requires a manual check'). Never fails the run."""
    results.append(("NOTE", label, detail))


def check_track(name, t):
    prefix = f"tracks.{name}"

    check(f"{prefix}.phase is a non-negative int",
          isinstance(t.get("phase"), int) and t.get("phase") >= 0,
          f"got {t.get('phase')!r}")

    exercises = t.get("completed_exercises", [])
    check(f"{prefix}.completed_exercises entries match P{{N}}-{{slug}}",
          all(isinstance(e, str) and SLUG.match(e) for e in exercises),
          f"got {exercises!r}")

    topic_confidence = t.get("topic_confidence", {})
    check(f"{prefix}.topic_confidence keys are kebab-case (Rule 10)",
          all(KEBAB.match(k) for k in topic_confidence),
          f"got keys {list(topic_confidence.keys())!r}")
    check(f"{prefix}.topic_confidence values are solid/shaky/struggling",
          all(v in CONFIDENCE_LEVELS for v in topic_confidence.values()),
          f"got {topic_confidence!r}")

    review_due = t.get("review_due", [])
    check(f"{prefix}.review_due entries are a subset of topic_confidence keys",
          all(k in topic_confidence for k in review_due),
          f"review_due={review_due!r} topic_confidence keys={list(topic_confidence.keys())!r}")
    warn(f"{prefix}.review_due has no 'solid' entries (Rule 6: cleared topics are removed)",
         all(topic_confidence.get(k) != "solid" for k in review_due),
         f"review_due={review_due!r}")

    observations = t.get("observations", "")
    check(f"{prefix}.observations is under 200 chars (Rule 4)",
          len(observations) < 200,
          f"len={len(observations)}")

    axis_overrides = t.get("axis_overrides", {})
    check(f"{prefix}.axis_overrides only uses known axis keys (Rule 7)",
          all(k in AXIS_KEYS for k in axis_overrides),
          f"got {axis_overrides!r}")

    low = t.get("low_hint_streak", 0)
    high = t.get("high_hint_streak", 0)
    check(f"{prefix}.low_hint_streak/high_hint_streak are non-negative ints",
          isinstance(low, int) and isinstance(high, int) and low >= 0 and high >= 0,
          f"low={low!r} high={high!r}")
    check(f"{prefix} streaks are mutually exclusive (Rule 8: incrementing one resets the other)",
          low == 0 or high == 0,
          f"low={low!r} high={high!r}")

    hint_count = t.get("hint_count", 0)
    check(f"{prefix}.hint_count is a non-negative int",
          isinstance(hint_count, int) and hint_count >= 0,
          f"got {hint_count!r}")

    next_up = t.get("next_up")
    current_exercise = t.get("current_exercise")
    if next_up is None:
        note(f"{prefix}.next_up is null -> should mean track completion (Step 6b point 8)",
             "verify manually that this track's curriculum has no exercises left")
    else:
        check(f"{prefix}.next_up looks like an exercise slug when not null",
              isinstance(next_up, str) and SLUG.match(next_up),
              f"got {next_up!r}")
    check(f"{prefix}.current_exercise looks like an exercise slug",
          current_exercise is None or (isinstance(current_exercise, str) and SLUG.match(current_exercise)),
          f"got {current_exercise!r}")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)

    project_dir = sys.argv[1]
    progress_path = os.path.join(project_dir, ".sage-progress.json")
    profile_path = os.path.join(project_dir, ".sage-profile.md")

    if not check("`.sage-progress.json` exists at project root",
                  os.path.isfile(progress_path), progress_path):
        print_report()
        sys.exit(1)

    with open(progress_path) as f:
        raw = f.read()
    try:
        data = json.loads(raw)
        check("`.sage-progress.json` is valid JSON", True)
    except json.JSONDecodeError as e:
        check("`.sage-progress.json` is valid JSON", False, str(e))
        print_report()
        sys.exit(1)

    check("top-level has 'active_track'", "active_track" in data)
    check("top-level has 'tracks'", isinstance(data.get("tracks"), dict))

    for name, t in data.get("tracks", {}).items():
        check_track(name, t)

    check("`.sage-profile.md` exists at project root (not inside skills/sage-instructor/references/)",
          os.path.isfile(profile_path), profile_path)

    print_report()
    sys.exit(0 if all(s != "FAIL" for s, _, _ in results) else 1)


def print_report():
    for status, label, detail in results:
        line = f"[{status}] {label}"
        if detail and status != "PASS":
            line += f"\n        {detail}"
        print(line)
    fails = sum(1 for s, _, _ in results if s == "FAIL")
    warns = sum(1 for s, _, _ in results if s == "WARN")
    notes = sum(1 for s, _, _ in results if s == "NOTE")
    print(f"\n{len(results)} checks, {fails} failed, {warns} warned, {notes} noted.")


if __name__ == "__main__":
    main()
