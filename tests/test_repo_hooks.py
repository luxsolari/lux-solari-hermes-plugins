import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipIf(os.name == 'nt', 'POSIX Git hooks require WSL/Git Bash')
class RepositoryHookTests(unittest.TestCase):
    def run_message(self, text):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as file:
            file.write(text)
            name = file.name
        try:
            return subprocess.run(['sh', str(ROOT / 'scripts/hooks/commit-msg'), name], capture_output=True, text=True)
        finally:
            Path(name).unlink()

    def push(self, remote_ref):
        env = dict(os.environ, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='whiting.defaultbranch', GIT_CONFIG_VALUE_0='main')
        line = f'refs/heads/topic {"a" * 40} {remote_ref} {"0" * 40}\n'
        return subprocess.run(['sh', str(ROOT / 'scripts/hooks/pre-push'), 'origin', 'unused'], input=line, env=env, cwd=ROOT, capture_output=True, text=True)

    def test_bad_message_rejected(self):
        self.assertNotEqual(self.run_message('add stuff\n').returncode, 0)

    def test_conventional_message_accepted(self):
        self.assertEqual(self.run_message('feat(release): publish checked tags\n').returncode, 0)

    def test_main_push_rejected(self):
        self.assertNotEqual(self.push('refs/heads/main').returncode, 0)

    def test_release_tag_push_allowed(self):
        self.assertEqual(self.push('refs/tags/v0.1.0').returncode, 0)

    def test_feature_branch_push_allowed(self):
        self.assertEqual(self.push('refs/heads/ci/whiting-releases').returncode, 0)
