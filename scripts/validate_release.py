"""Validate a release and print its changelog notes (no publishing side effects)."""
import argparse
import re
from pathlib import Path

from extract_changelog import extract


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('tag')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    if not re.fullmatch(r'v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', args.tag):
        raise SystemExit('Expected a canonical vX.Y.Z release tag')
    version = args.tag.removeprefix('v')
    if (args.root / 'VERSION').read_text().strip() != version:
        raise SystemExit('VERSION does not match the release tag')
    notes = extract((args.root / 'CHANGELOG.md').read_text(), version)
    if not notes.strip():
        raise SystemExit('Release notes are empty')
    print(notes, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
