"""Run with Hermes's Python runtime; scans without installing or enabling anything."""
import argparse
import json
from pathlib import Path

from tools.skill_manager_tool import _validate_frontmatter
from tools.skills_guard import scan_skill


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    rows = []
    for folder in sorted((args.root / 'skills').iterdir()):
        if not (folder / 'SKILL.md').is_file():
            continue
        text = (folder / 'SKILL.md').read_text()
        scan = scan_skill(folder, source='community')
        rows.append({
            'name': folder.name,
            'frontmatter_error': _validate_frontmatter(text),
            'verdict': scan.verdict,
            'findings': [vars(item) for item in scan.findings],
        })
    print(json.dumps(rows, indent=2, default=str))
    return int(any(row['frontmatter_error'] for row in rows))


if __name__ == '__main__':
    raise SystemExit(main())
