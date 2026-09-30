#!/usr/bin/env python3
"""
Checks whether the upstream three-axes-framework plugin's SKILL.md has
changed since references/philosophy.md was last adapted from it.

philosophy.md is NOT a copy of the upstream file -- it's a teaching-specific
adaptation (lesson-step calibration, curriculum-generation axis inference,
etc. that don't exist upstream). So this script never overwrites
philosophy.md automatically. It only diffs the upstream source against a
cached snapshot of the last-reviewed version, and tells you to go reconcile
by hand if something changed.

Usage:
    python3 scripts/check_framework_drift.py
        Fetch upstream, diff against the cached snapshot, print the result.
        Exits 1 if drift is found, 0 if clean (a network failure also exits
        1, with a message distinguishing it from real drift).

    python3 scripts/check_framework_drift.py --update-snapshot
        After manually reconciling philosophy.md against upstream changes,
        run this to accept the current upstream content as the new
        baseline snapshot.
"""
import difflib
import sys
import urllib.request
from pathlib import Path

UPSTREAM_URL = "https://raw.githubusercontent.com/luxsolari/three-axes-framework/main/skills/three-axes-framework/SKILL.md"
SNAPSHOT_PATH = Path(__file__).resolve().parent.parent / "references" / ".three-axes-upstream-snapshot.md"


def fetch_upstream() -> str:
    with urllib.request.urlopen(UPSTREAM_URL, timeout=10) as response:
        return response.read().decode("utf-8")


def main() -> int:
    # Windows consoles default stdout to the system codepage (e.g. cp1252),
    # which can't encode characters like "↓" in SKILL.md's tier diagram --
    # crashing exactly when there's a real diff to show. Force UTF-8 output
    # regardless of platform/terminal default.
    sys.stdout.reconfigure(encoding="utf-8")

    update_snapshot = "--update-snapshot" in sys.argv

    try:
        upstream = fetch_upstream()
    except Exception as e:
        print(f"Could not fetch upstream three-axes-framework SKILL.md: {e}")
        print(f"URL: {UPSTREAM_URL}")
        return 1

    snapshot = SNAPSHOT_PATH.read_text(encoding="utf-8") if SNAPSHOT_PATH.exists() else ""

    if upstream == snapshot:
        print("No drift -- upstream three-axes-framework matches the last-reviewed snapshot.")
        return 0

    if update_snapshot:
        SNAPSHOT_PATH.write_text(upstream, encoding="utf-8")
        print(f"Snapshot updated: {SNAPSHOT_PATH}")
        return 0

    print("Upstream three-axes-framework has changed since the last review.")
    print(f"Source: {UPSTREAM_URL}")
    print("This does NOT mean philosophy.md is wrong -- it's an adaptation, not a")
    print("copy. Review the diff below, decide whether the change is relevant to")
    print("teaching contexts, update references/philosophy.md")
    print("by hand if so, then re-run with --update-snapshot to accept the new baseline.\n")
    diff = difflib.unified_diff(
        snapshot.splitlines(keepends=True),
        upstream.splitlines(keepends=True),
        fromfile="snapshot (last reviewed)",
        tofile="upstream (current)",
    )
    sys.stdout.writelines(diff)
    return 1


if __name__ == "__main__":
    sys.exit(main())
