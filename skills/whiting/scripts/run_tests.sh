#!/bin/sh
# Runs every test in tests/: python unittest files and POSIX shell test scripts.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
test_root="${1:-$root/tests}"
[ -d "$test_root" ] || { printf '%s\n' 'Development tests are not installed. Run repository scripts/run_checks.py.' >&2; exit 2; }
fail=0

for test_file in "$test_root"/test_*.py; do
    [ -e "$test_file" ] || continue
    echo "== $test_file =="
    python3 "$test_file" || fail=1
done

for test_file in "$test_root"/test_*.sh; do
    [ -e "$test_file" ] || continue
    echo "== $test_file =="
    sh "$test_file" || fail=1
done

if [ "$fail" -eq 0 ]; then
    echo "All tests passed."
else
    echo "Some tests failed." >&2
fi
exit "$fail"
