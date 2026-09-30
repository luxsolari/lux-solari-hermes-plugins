"""Release gate exercises real files and the CLI."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/validate_release.py'


class ReleaseGateTests(unittest.TestCase):
    def run_gate(self, tag='v0.1.0', version='0.1.0', notes='### Added\n- Initial tap.\n'):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / 'VERSION').write_text(version + '\n')
            (folder / 'CHANGELOG.md').write_text('# Changelog\n\n## [Unreleased]\n\n## [0.1.0] — 2026-09-29\n\n' + notes)
            return subprocess.run([sys.executable, str(SCRIPT), tag, '--root', str(folder)], capture_output=True, text=True)

    def test_noncanonical_tag_is_rejected(self):
        for tag in ['0.1.0', 'vv0.1.0', 'v00.1.0', 'v0.1.0; touch injected']:
            with self.subTest(tag=tag):
                result = self.run_gate(tag=tag)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('canonical', result.stderr)

    def test_version_mismatch_is_rejected(self):
        result = self.run_gate(version='0.2.0')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('VERSION', result.stderr)

    def test_empty_release_notes_are_rejected(self):
        result = self.run_gate(notes='\n')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('empty', result.stderr)

    def test_matching_release_prints_only_version_notes(self):
        result = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '### Added\n- Initial tap.\n')


if __name__ == '__main__':
    unittest.main()
