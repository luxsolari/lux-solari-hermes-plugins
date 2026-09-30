# Hannah engine (Hermes skill bundle)

The shipped Python package is version 0.10.6. Python 3.11+; no third-party
runtime dependencies. Engine source and `pyproject.toml` are in this directory.

Run without installation from this directory:

```sh
python3 -m hannah /absolute/path/to/repo --json
```

From another POSIX workdir use `sh /absolute/skill/root/scripts/run-hannah ...`.
Install this directory in a venv with `python -m pip install /absolute/skill/root`,
not the similarly named PyPI package. Setuptools and wheel are build dependencies.
See `SKILL.md` for Windows invocation, hardware overrides, and safeguards.

Offline tests: `python3 -m unittest discover -s tests -v`. The added CLI test
executes real analysis/reporting with external metadata mocked and network denied;
normal analysis performs best-effort network metadata lookups and has no offline
flag. It does not download model weights.

Rankings are estimates, not guaranteed fits. In particular upstream fallback and
Apple selection can include oversized/platform-incompatible candidates; verify
memory overhead, runner support, model tags/IDs, and workload quality separately.
`references/strategy.md` defines the preserved F1 report format.

Upstream README is retained unchanged in `references/source-README.md` for
provenance, not as Hermes installation guidance. Code license: MIT (`LICENSE`).
