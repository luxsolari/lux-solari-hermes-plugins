"""Offline release/update regressions; no user config or network access."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("three_axes_sync", ROOT / "scripts/sync_three_axes.py")
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


def release(version="1.7.3", **kwargs):
    return dict(tag_name="three-axes-framework-v" + version, draft=False,
                prerelease=False, published_at="2026-10-26T00:00:00Z", **kwargs)


class ReleaseSyncTests(unittest.TestCase):
    def fixture(self, root, kind):
        old = b"---\nname: three-axes-framework\n---\n\n# Framework\n\nRule before.\n\nStable context one.\nStable context two.\nStable context three.\nStable context four.\n"
        blobs = {sync.SKILL: old, sync.MANIFEST: sync.encode(dict(name="three-axes-framework", version="1.7.2")),
                 "hooks/start.mjs": b"trusted hook\n", "commands/three-axes.md": b"command\n",
                 "LICENSE": b"MIT\n", "CHANGELOG.md": b"# Upstream notes\n"}
        prefix, skill = sync.host_paths(kind)
        files = {sync.BASE: old, "CHANGELOG.md": b"# Changelog\n\n## [Unreleased]\n",
                 "JOURNAL.md": b"# Journal\n\n## Earlier evidence\n\nPreserve.\n"}
        if kind == "claude":
            files[".claude-plugin/marketplace.json"] = sync.encode(dict(plugins=[
                dict(name="three-axes-framework", source=dict(source="github", repo=sync.UPSTREAM, ref="three-axes-framework-v1.7.2", sha="a" * 40)),
                dict(name="unrelated", source="./unchanged")]))
            managed = {}
        else:
            files[skill] = old + b"\nHost-specific instructions.\n"
            if kind == "codex":
                files[prefix + "/.codex-plugin/plugin.json"] = sync.encode(dict(name="three-axes-framework", version="1.7.2", interface=dict(displayName="Three Axes Framework")))
            else:
                files[skill] = files[skill].replace(b"name: three-axes-framework\n", b"name: three-axes-framework\nversion: 1.7.2\n")
                files["SOURCE.json"] = sync.encode(dict(repository="original", additional_sources={"three-axes-framework": dict(repository="https://github.com/" + sync.UPSTREAM, revision="a" * 40, tag="three-axes-framework-v1.7.2", sha256={p: sync.digest(b) for p, b in blobs.items()})}))
            managed = {p: sync.digest(b) for p, b in files.items() if p.startswith(prefix + "/")}
        files[sync.STATE] = sync.encode(dict(host=kind, version="1.7.2", tag="three-axes-framework-v1.7.2", revision="a" * 40,
                  source_files={p: sync.digest(b) for p, b in blobs.items()}, managed_files=managed,
                  manifest_contract=dict(name="three-axes-framework")))
        sync.apply(root, files)
        return blobs

    def incoming(self, blobs, version="1.7.3"):
        return dict(blobs, **{sync.MANIFEST: sync.encode(dict(name="three-axes-framework", version=version)),
                             sync.SKILL: blobs[sync.SKILL].replace(b"Rule before.", b"Rule after.")})

    def test_update_preserves_host_adapters_and_is_idempotent(self):
        for kind in ("codex", "claude", "hermes"):
            with self.subTest(host=kind), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                before = self.fixture(root, kind)
                incoming = self.incoming(before)
                updates = sync.plan(root, release(), "b" * 40, incoming)
                sync.apply(root, updates)
                self.assertEqual(sync.check(root)["version"], "1.7.3")
                self.assertEqual(sync.plan(root, release(), "b" * 40, incoming), {})
                self.assertIn("Earlier evidence", (root / "JOURNAL.md").read_text())
                if kind == "claude":
                    catalog = json.loads((root / ".claude-plugin/marketplace.json").read_text())
                    self.assertEqual(catalog["plugins"][1], dict(name="unrelated", source="./unchanged"))
                else:
                    _, skill = sync.host_paths(kind)
                    text = (root / skill).read_text()
                    self.assertIn("Host-specific instructions.", text)
                    self.assertIn("Rule after.", text)
                    self.assertNotIn("Rule before.", text)

    def assert_refused(self, mutate, pattern):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            blobs = self.fixture(root, "codex")
            incoming = self.incoming(blobs)
            meta, revision = release(), "b" * 40
            override = mutate(root, incoming, meta)
            if override:
                revision = override
            before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            with self.assertRaisesRegex((ValueError, KeyError), pattern):
                sync.plan(root, meta, revision, incoming)
            after = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            self.assertEqual(before, after, "a refused plan must leave every checkout byte untouched")

    def test_tag_and_manifest_version_must_match(self):
        self.assert_refused(lambda r, b, m: b.update({sync.MANIFEST: sync.encode(dict(name="three-axes-framework", version="9.0.0"))}), "disagree")

    def test_same_version_cannot_be_rewritten(self):
        self.assert_refused(lambda r, b, m: (m.update(tag_name="three-axes-framework-v1.7.2"), b.update({sync.MANIFEST: sync.encode(dict(name="three-axes-framework", version="1.7.2"))})) and None, "rewritten")

    def test_downgrade_refuses(self):
        self.assert_refused(lambda r, b, m: (m.update(tag_name="three-axes-framework-v1.7.1"), b.update({sync.MANIFEST: sync.encode(dict(name="three-axes-framework", version="1.7.1"))})) and None, "downgrade")

    def test_draft_prerelease_and_unpublished_refuse(self):
        for field, value in (("draft", True), ("prerelease", True), ("published_at", None)):
            self.assert_refused(lambda r, b, m: m.update({field: value}), "published stable")

    def test_ref_injection_and_noncanonical_versions_refuse(self):
        for tag in ("--upload-pack=bad", "three-axes-framework-v01.7.3", "three-axes-framework-v1.7.3-rc1"):
            self.assert_refused(lambda r, b, m: m.update(tag_name=tag), "published stable")

    def test_new_runtime_file_requires_mapping_review(self):
        self.assert_refused(lambda r, b, m: b.update({"skills/new/SKILL.md": b"unreviewed"}), "layout changed")

    def test_changed_hooks_require_manual_adapter_review(self):
        self.assert_refused(lambda r, b, m: b.update({"hooks/start.mjs": b"new behavior"}), "hooks changed")

    def test_manifest_contract_changes_require_review(self):
        self.assert_refused(lambda r, b, m: b.update({sync.MANIFEST: sync.encode(dict(name="three-axes-framework", version="1.7.3", commands=["new/"]))}), "contract changed")

    def test_dirty_managed_file_is_not_overwritten(self):
        self.assert_refused(lambda r, b, m: (r / sync.host_paths("codex")[1]).write_bytes(b"local change") and None, "managed file drift")

    def test_conflicting_skill_edit_refuses(self):
        self.assert_refused(lambda r, b, m: b.update({sync.SKILL: b"different document\n"}), "conflicts")

    def test_conversational_translation_refuses_missing_or_ambiguous_passage(self):
        for current in (b"host translation\n", b"Rule before.\nRule before.\n"):
            with self.assertRaisesRegex(ValueError, "manual conversational"):
                sync.update_conversational_skill(current, b"Rule before.\n", b"Rule after.\n")

    def test_managed_paths_cannot_escape(self):
        for path in ("../escape", "/absolute", "C:/outside", "a\\..\\outside"):
            with self.assertRaises(ValueError):
                sync.local(ROOT, path)

    def test_current_release_has_execution_context_rule_and_shared_identity(self):
        lock = sync.check(ROOT)
        self.assertEqual(lock["revision"], "cd0bc9066ad064c58a6981d93a1c4d34107a018b" if lock["version"] == "1.7.2" else lock["revision"])
        prefix, skill = sync.host_paths(lock["host"])
        path = skill if skill else sync.BASE
        text = (ROOT / path).read_text(encoding="utf-8")
        self.assertIn("relevant working-tree context", text)
        self.assertIn("name: three-axes-framework\n", text)
        if lock["host"] == "hermes":
            self.assertIn("not** an automatic tool-denial hook", text)

    def test_workflow_dispatches_ci_without_merging(self):
        text = (ROOT / ".github/workflows/sync-three-axes.yml").read_text()
        self.assertIn("schedule:", text)
        self.assertIn("gh workflow run", text)
        self.assertIn("--ref", text)
        self.assertNotIn("gh pr merge", text)
        self.assertNotIn("pull_request_target", text)

    @unittest.skipIf(os.name == "nt", "workflow shell executes on the hosted Linux runner")
    def test_bot_workflow_recovers_pr_and_dispatch_and_preserves_existing_head(self):
        """Execute the real workflow shell against isolated GitHub/Git responses."""
        workflow = (ROOT / ".github/workflows/sync-three-axes.yml").read_text()
        shell = workflow.split("        run: |\n", 1)[1]
        shell = "\n".join(line[10:] for line in shell.splitlines()) + "\n"
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "maintenance/three-axes").mkdir(parents=True)
            (root / sync.STATE).write_text('{"version":"1.7.3"}')
            (root / "run.sh").write_text(shell)
            binary = root / "bin"
            binary.mkdir()
            mock = '''import json, os, sys
from pathlib import Path
tool = Path(sys.argv[0]).name
args = sys.argv[1:]
with open(os.environ['CALL_LOG'], 'a') as log:
    log.write(json.dumps([tool, *args]) + '\\n')
if tool == 'git':
    if args[:2] == ['diff', '--quiet']:
        sys.exit(1)
    if args[0] == 'ls-remote':
        if os.environ['BRANCH_EXISTS'] == '1':
            print('b' * 40 + '\\trefs/heads/codex/sync-three-axes-1.7.3')
        else:
            sys.exit(2)
elif args[:2] == ['pr', 'list']:
    print(os.environ['PR_STATE'])
elif args[:2] == ['run', 'list']:
    # An approval-pending PR run must not suppress explicit CI dispatch.
    assert '--event' in args and args[args.index('--event') + 1] == 'workflow_dispatch'
    print(os.environ['DISPATCH_RUNS'])
'''
            for name in ("git", "gh"):
                path = binary / name
                path.write_text("#!" + sys.executable + "\n" + mock)
                path.chmod(0o755)
            for exists, state, runs in (("0", "MISSING", "0"), ("1", "MISSING", "0"), ("1", "OPEN", "0"), ("1", "OPEN", "1"), ("1", "CLOSED", "0")):
                with self.subTest(branch=exists, pr=state, ci=runs):
                    log = root / "calls.jsonl"
                    log.write_text("")
                    env = dict(os.environ, PATH=str(binary) + os.pathsep + os.environ["PATH"],
                               RUNNER_TEMP=str(root), CALL_LOG=str(log), BRANCH_EXISTS=exists,
                               PR_STATE=state, DISPATCH_RUNS=runs)
                    result = subprocess.run(["bash", "run.sh"], cwd=root, env=env, capture_output=True, text=True)
                    calls = [json.loads(line) for line in log.read_text().splitlines()]
                    if state == "CLOSED":
                        self.assertNotEqual(result.returncode, 0)
                        continue
                    self.assertEqual(result.returncode, 0, result.stderr)
                    pushes = [c for c in calls if c[:2] == ["git", "push"]]
                    self.assertEqual(len(pushes), int(exists == "0"))
                    self.assertTrue(all(c[-1] != "main" and "--force" not in c for c in pushes))
                    creates = [c for c in calls if c[:3] == ["gh", "pr", "create"]]
                    self.assertEqual(len(creates), int(state == "MISSING"))
                    dispatches = [c for c in calls if c[:3] == ["gh", "workflow", "run"]]
                    self.assertEqual(len(dispatches), int(runs == "0"))
                    self.assertTrue(all("--ref" in c and c[-1] == "codex/sync-three-axes-1.7.3" for c in dispatches))


if __name__ == "__main__":
    unittest.main()
