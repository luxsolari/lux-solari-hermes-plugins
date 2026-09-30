"""Offline package-contract tests; not a claim of model-behavior parity."""
import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
NAMES = {
    'three-axes-framework', 'sage-instructor', 'whiting', 'hannah',
    'lux-swiss', 'tri-swiss', 'anime-identity-designer',
    'lux-visual-systems', 'machine-pilgrim',
}


class TapContractTests(unittest.TestCase):
    def test_inventory(self):
        self.assertEqual({p.parent.name for p in (ROOT / 'skills').glob('*/SKILL.md')}, NAMES)

    def test_frontmatter_and_required_sections(self):
        for name in sorted(NAMES):
            with self.subTest(skill=name):
                text = (ROOT / 'skills' / name / 'SKILL.md').read_text()
                self.assertTrue(text.startswith('---\n'))
                header, body = text[4:].split('\n---\n', 1)
                fm = yaml.safe_load(header)
                self.assertEqual(fm['name'], name)
                self.assertIsInstance(fm['description'], str)
                self.assertLessEqual(len(fm['description']), 60)
                self.assertTrue(fm['description'].endswith('.'))
                for key in ('version', 'author', 'license', 'platforms'):
                    self.assertIn(key, fm)
                for related in fm.get('metadata', {}).get('hermes', {}).get('related_skills', []):
                    self.assertIn(related, NAMES)
                for section in ('When to Use', 'Pitfalls', 'Verification'):
                    self.assertIn('## ' + section, body)
                self.assertNotIn('/home/luxsolari', text)

    def test_explicit_support_paths_exist(self):
        pattern = re.compile(r'`((?:references|assets|scripts|templates|curricula)/[^`\n]+)`')
        for name in sorted(NAMES):
            folder = ROOT / 'skills' / name
            text = (folder / 'SKILL.md').read_text()
            for rel in pattern.findall(text):
                # Inline command examples can include arguments after a script.
                rel = re.split(r'(?<=\.py)\s|(?<=\.sh)\s', rel, maxsplit=1)[0]
                if any(c in rel for c in '*<>') or rel.endswith('/'):
                    continue
                with self.subTest(skill=name, path=rel):
                    self.assertTrue((folder / rel).exists(), rel)

    def test_visual_assets_and_licenses_ship(self):
        expected = {'anime-identity-designer': 13, 'lux-visual-systems': 22, 'machine-pilgrim': 18}
        for name, count in expected.items():
            folder = ROOT / 'skills' / name
            with self.subTest(skill=name):
                self.assertEqual(len(list((folder / 'assets').glob('*.png'))), count)
                self.assertTrue((folder / 'LICENSE-DESIGN').is_file())
                self.assertTrue((folder / 'NOTICE.md').is_file())

    def test_hannah_engine_ships(self):
        folder = ROOT / 'skills' / 'hannah'
        self.assertTrue((folder / 'hannah' / '__main__.py').is_file())
        self.assertTrue((folder / 'pyproject.toml').is_file())

    def test_sage_snapshot_is_downloadable(self):
        snapshot = ROOT / 'skills/sage-instructor/references/three-axes-upstream-snapshot.md'
        self.assertTrue(snapshot.is_file())
        self.assertFalse(snapshot.name.startswith('.'))

    def test_no_symlinks_or_generated_python(self):
        for path in (ROOT / 'skills').rglob('*'):
            self.assertFalse(path.is_symlink(), str(path))
            self.assertNotEqual(path.suffix, '.pyc', str(path))


if __name__ == '__main__':
    unittest.main()
