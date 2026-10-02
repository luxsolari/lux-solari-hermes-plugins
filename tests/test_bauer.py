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
REVISION = 'fc7ba2eb8f4f91cc12f27fb3c0655c519127691d'
FILES = {
    'SKILL.md', 'references/advisories.md', 'references/jev.md',
    'references/report.md', 'references/security-sources.json',
    'references/supply-chain.md', 'scripts/dependencies.py', 'scripts/jev.py',
    'scripts/report.py', 'scripts/sources.py', 'scripts/selection.py', 'scripts/completion.py', 'scripts/control.py', 'scripts/profiles.py',
    'scripts/run_record.py', 'scripts/scorecard.py', 'LICENSE', 'NOTICE.md',
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
        self.assertEqual(provenance['version'], '0.3.0')
        paths = {rel if rel in {'LICENSE', 'NOTICE.md'} else 'skills/bauer/' + rel: rel
                 for rel in FILES}
        self.assertEqual(set(provenance['sha256']), set(paths))
        for source, rel in sorted(paths.items()):
            with self.subTest(source=source):
                self.assertEqual(hashlib.sha256((SKILL / rel).read_bytes()).hexdigest(),
                                 provenance['sha256'][source])

    def test_bundled_helper_help_is_local_and_executable(self):
        for name in ('dependencies', 'jev', 'report', 'sources', 'selection', 'control'):
            with self.subTest(helper=name):
                result = subprocess.run([sys.executable, '-B', str(SKILL / 'scripts' / (name + '.py')), '--help'],
                                        capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('usage:', result.stdout)

        fixture = dict(scope='synthetic package contract', sources=[], coverage=[],
                       limitations=['Synthetic only; no queries'], findings=[])
        with tempfile.TemporaryDirectory() as folder:
            evidence = Path(folder) / 'evidence.json'
            evidence.write_text(json.dumps(fixture))
            control = SKILL / 'scripts/control.py'
            pending = Path(folder) / 'pending.json'
            confirmed = Path(folder) / 'confirmed.json'
            first = subprocess.run([sys.executable, '-B', str(control), 'preflight', '--output', str(pending)],
                                   capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(first.stdout)['status'], 'pending_confirmation')
            subprocess.run([sys.executable, '-B', str(control), 'confirm', '--run-record', str(pending),
                            '--decision', 'confirm', '--user-response', 'Synthetic package fixture confirmation',
                            '--response-ref', 'fixture:second-turn', '--output', str(confirmed)],
                           capture_output=True, text=True, check=True)
            for fmt in ('json', 'markdown'):
                run = subprocess.run([sys.executable, '-B', str(SKILL / 'scripts/report.py'), str(evidence), '--run-record', str(confirmed), '--format', fmt],
                                     capture_output=True, text=True, timeout=10)
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertIn('Security audits can be token-intensive', run.stdout)
                if fmt == 'json':
                    gate = json.loads(run.stdout)['completion_gate']
                    self.assertEqual(gate['status'], 'partial')
                    self.assertEqual(len(gate['obligations']), 15)
                    self.assertTrue(all(row['status'] == 'unattempted' for row in gate['obligations'] if row['selected']))
                else:
                    self.assertIn('Overall: partial', run.stdout)
                    self.assertIn('dependency&#95;coverage', run.stdout)



if __name__ == '__main__':
    unittest.main()
