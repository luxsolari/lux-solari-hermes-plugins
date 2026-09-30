"""Exercise packaging and helper suites offline, with user Git configuration isolated."""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    env = os.environ.copy()
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['GIT_CONFIG_GLOBAL'] = os.devnull
    env['GIT_CONFIG_NOSYSTEM'] = '1'
    env['GIT_TERMINAL_PROMPT'] = '0'
    for key in ('GH_TOKEN', 'GITHUB_TOKEN', 'GH_ENTERPRISE_TOKEN', 'GITHUB_ENTERPRISE_TOKEN'):
        env.pop(key, None)
    total = 0
    failures = []
    with tempfile.TemporaryDirectory(prefix='hermes-port-tests-') as scratch:
        env['GH_CONFIG_DIR'] = scratch
        suites = [(ROOT / 'tests', ROOT)]
        suites += [(p / 'tests', p) for p in sorted((ROOT / 'skills').iterdir()) if (p / 'tests').is_dir()]
        suites += [(ROOT / 'tests/whiting', ROOT / 'skills/whiting')]
        for tests, cwd in suites:
            label = str(tests.relative_to(ROOT))
            result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(tests), '-v'], cwd=cwd, env=env, capture_output=True, text=True)
            output = result.stdout + result.stderr
            matches = re.findall(r'Ran (\d+) tests?', output)
            count = sum(map(int, matches))
            total += count
            print(f'{label}: {count} Python tests, exit {result.returncode}', flush=True)
            if result.returncode:
                print(output)
                failures.append(label)
        shells = sorted((ROOT / 'tests/whiting').glob('test_*.sh')) if os.name != 'nt' else []
        for script in shells:
            result = subprocess.run(['sh', str(script)], cwd=ROOT / 'skills/whiting', env=env, capture_output=True, text=True)
            print(f'{script.name}: exit {result.returncode}', flush=True)
            if result.returncode:
                print(result.stdout + result.stderr)
                failures.append(script.name)
    print(f'Total: {total} Python tests; {len(shells)} shell suites; failures: {failures}')
    return int(bool(failures))


if __name__ == '__main__':
    raise SystemExit(main())
