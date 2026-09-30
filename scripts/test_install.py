"""Live GitHub tap-install smoke test in disposable Hermes homes (never the active profile)."""
import hashlib
import json
import os
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check(folder):
    with tempfile.TemporaryDirectory(prefix='hermes-port-install-') as home:
        env = dict(os.environ, HERMES_HOME=home, PYTHONDONTWRITEBYTECODE='1')
        # Reuse the existing gh login without printing or persisting its token.
        if not env.get('GITHUB_TOKEN') and not env.get('GH_TOKEN'):
            auth = subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True)
            if auth.returncode == 0:
                env['GH_TOKEN'] = auth.stdout.strip()
        result = subprocess.run(['hermes', 'skills', 'install', f'luxsolari/lux-solari-hermes-plugins/skills/{folder.name}', '--yes'], env=env, capture_output=True, text=True, timeout=300)
        roots = list((Path(home) / 'skills').rglob(folder.name + '/SKILL.md'))
        missing, changed = [], []
        checked = 0
        if len(roots) == 1:
            target = roots[0].parent
            for source in folder.rglob('*'):
                if not source.is_file():
                    continue
                rel = source.relative_to(folder)
                if source.name.startswith('.') or source.suffix == '.pyc' or '__pycache__' in rel.parts:
                    continue  # Hermes's documented installer exclusions
                installed = target / rel
                checked += 1
                if not installed.is_file():
                    missing.append(str(rel))
                elif hashlib.sha256(source.read_bytes()).digest() != hashlib.sha256(installed.read_bytes()).digest():
                    changed.append(str(rel))
        else:
            missing.append('unique installed SKILL.md')
        return {'name': folder.name, 'exit_code': result.returncode, 'files_checked': checked, 'missing': missing, 'changed': changed, 'output': result.stdout + result.stderr}


def main():
    folders = sorted(p for p in (ROOT / 'skills').iterdir() if (p / 'SKILL.md').is_file())
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(check, folders))
    report = Path(os.environ.get('TMPDIR', tempfile.gettempdir())) / 'hermes-port-install-results.json'
    report.write_text(json.dumps(results, indent=2))
    for r in results:
        print({k: v for k, v in r.items() if k != 'output'})
        if r['exit_code'] or r['missing'] or r['changed']:
            print(r['output'])
    print('Report:', report)
    return int(any(r['exit_code'] or r['missing'] or r['changed'] for r in results))


if __name__ == '__main__':
    raise SystemExit(main())
