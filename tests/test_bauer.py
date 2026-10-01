"""Bauer's canonical-source packaging contract; no network or active installation."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/bauer'
REVISION = '08320e9155850cbd9b4be2f2051eb62bf4247f81'
FILES = {
    'SKILL.md', 'references/advisories.md', 'references/jev.md',
    'references/report.md', 'references/security-sources.json',
    'references/supply-chain.md', 'scripts/dependencies.py', 'scripts/jev.py',
    'scripts/report.py', 'scripts/sources.py', 'scripts/selection.py', 'scripts/completion.py', 'LICENSE', 'NOTICE.md',
}


class BauerContractTests(unittest.TestCase):
    def test_complete_downloadable_inventory(self):
        actual = {p.relative_to(SKILL).as_posix() for p in SKILL.rglob('*') if p.is_file()}
        self.assertEqual(actual, FILES)
        for rel in actual:
            self.assertFalse(any(part.startswith('.') for part in Path(rel).parts), rel)

    def test_canonical_source_provenance_and_byte_parity(self):
        provenance = json.loads((ROOT / 'SOURCE.json').read_text())['additional_sources']['bauer']
        self.assertEqual(provenance['repository'], 'https://github.com/luxsolari/bauer')
        self.assertEqual(provenance['revision'], REVISION)
        self.assertEqual(provenance['version'], '0.2.1')
        paths = {rel if rel in {'LICENSE', 'NOTICE.md'} else 'skills/bauer/' + rel: rel
                 for rel in FILES}
        self.assertEqual(set(provenance['sha256']), set(paths))
        for source, rel in sorted(paths.items()):
            with self.subTest(source=source):
                self.assertEqual(hashlib.sha256((SKILL / rel).read_bytes()).hexdigest(),
                                 provenance['sha256'][source])

    def test_bundled_helper_help_is_local_and_executable(self):
        for name in ('dependencies', 'jev', 'report', 'sources', 'selection'):
            with self.subTest(helper=name):
                result = subprocess.run([sys.executable, str(SKILL / 'scripts' / (name + '.py')), '--help'],
                                        capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('usage:', result.stdout)

        fixture = dict(scope='synthetic package contract', sources=[], coverage=[],
                       limitations=['Synthetic only; no queries'], findings=[])
        with tempfile.TemporaryDirectory() as folder:
            evidence = Path(folder) / 'evidence.json'
            evidence.write_text(json.dumps(fixture))
            for fmt in ('json', 'markdown'):
                run = subprocess.run([sys.executable, str(SKILL / 'scripts/report.py'), str(evidence), '--format', fmt],
                                     capture_output=True, text=True, timeout=10)
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertIn('Security audits can be token-intensive', run.stdout)
                if fmt == 'json':
                    gate = json.loads(run.stdout)['completion_gate']
                    self.assertEqual(gate['status'], 'partial')
                    self.assertEqual(len(gate['obligations']), 15)
                    self.assertTrue(all(row['status'] == 'unattempted' for row in gate['obligations']))
                else:
                    self.assertIn('Overall: partial', run.stdout)
                    self.assertIn('dependency&#95;coverage', run.stdout)



if __name__ == '__main__':
    unittest.main()
