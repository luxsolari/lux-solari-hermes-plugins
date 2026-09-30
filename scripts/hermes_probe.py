"""Run with Hermes's Python runtime; scans without installing or enabling anything."""
import argparse
import json
from pathlib import Path

from tools.skill_manager_tool import _validate_frontmatter
from tools.skills_guard import scan_skill
from tools.skills_hub_models import _referenced_support_paths


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
            'support_parser_accepted': _referenced_support_paths(text) is not None,
            'referenced_directories': [rel for rel in (_referenced_support_paths(text) or []) if (folder / rel).is_dir()],
            'frontmatter_error': _validate_frontmatter(text),
            'verdict': scan.verdict,
            'findings': [vars(item) for item in scan.findings],
        })
    print(json.dumps(rows, indent=2, default=str))
    return int(any(row['frontmatter_error'] or not row['support_parser_accepted'] or row['referenced_directories'] for row in rows))


if __name__ == '__main__':
    raise SystemExit(main())
