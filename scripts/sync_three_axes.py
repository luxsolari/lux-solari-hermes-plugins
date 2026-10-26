"""Synchronize a host adaptation from an immutable, published open release.

Only release metadata and Git blobs are consumed. No upstream code is executed.
Unknown runtime layouts, changed hooks, or conflicting host edits require review.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
import urllib.request

UPSTREAM = "luxsolari/three-axes-framework"
SKILL = "skills/three-axes-framework/SKILL.md"
MANIFEST = ".claude-plugin/plugin.json"
STATE = "maintenance/three-axes/release.json"
BASE = "maintenance/three-axes/source-SKILL.md"
TAG = re.compile(r"three-axes-framework-v((?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*))\Z")


def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def digest(data):
    # Git text blobs and platform checkouts have identical logical content.
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def local(root, rel):
    path = PurePosixPath(rel)
    if path.is_absolute() or ".." in path.parts or "\\" in rel or ":" in rel:
        raise ValueError("unsafe managed path")
    target = root.joinpath(*path.parts)
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError("managed path leaves checkout")
    if any(p.is_symlink() for p in (target, *target.parents)):
        raise ValueError("linked managed path")
    return target


def api_release():
    request = urllib.request.Request(
        f"https://api.github.com/repos/{UPSTREAM}/releases/latest",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "three-axes-marketplace-sync"},
    )
    token = os.environ.get("GH_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def release_version(release):
    match = TAG.fullmatch(release.get("tag_name", ""))
    if (not match or release.get("draft") is not False
            or release.get("prerelease") is not False or not release.get("published_at")):
        raise ValueError("expected a published stable Three Axes release")
    return match[1]


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True).stdout


def source_blobs(repo, revision):
    result = {}
    for entry in git(repo, "ls-tree", "-r", "-z", revision).split(b"\0"):
        if not entry:
            continue
        info, raw_path = entry.split(b"\t", 1)
        path = raw_path.decode("utf-8")
        if not (path.startswith(("skills/", "commands/", "hooks/", "agents/", "scripts/",
                                 "templates/", "outputStyles/", ".claude-plugin/", ".codex-plugin/"))
                or path in (".mcp.json", ".lsp.json", ".app.json", "hooks.json", "LICENSE", "CHANGELOG.md")):
            continue
        mode, kind, oid = info.split()
        if mode not in (b"100644", b"100755") or kind != b"blob":
            raise ValueError("upstream runtime includes a link or non-file")
        result[path] = git(repo, "cat-file", "blob", oid.decode())
    return result


def merge_skill(current, baseline, incoming):
    with tempfile.TemporaryDirectory(prefix="three-axes-merge-") as folder:
        paths = [Path(folder) / name for name in ("host", "base", "release")]
        for path, data in zip(paths, (current, baseline, incoming)):
            path.write_bytes(data.replace(b"\r\n", b"\n"))
        result = subprocess.run(["git", "merge-file", "-p", *map(str, paths)], capture_output=True)
        if result.returncode:
            raise ValueError("upstream skill conflicts with the host adaptation; review manually")
        return result.stdout


def update_conversational_skill(current, baseline, incoming):
    """Replay exact changed source passages; never invent a host translation."""
    old = baseline.decode("utf-8").replace("\r\n", "\n").splitlines(keepends=True)
    new = incoming.decode("utf-8").replace("\r\n", "\n").splitlines(keepends=True)
    text = current.decode("utf-8").replace("\r\n", "\n")
    for op, a, b, c, d in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
        if op == "equal":
            continue
        before, after = "".join(old[a:b]), "".join(new[c:d])
        if not before or text.count(before) != 1:
            raise ValueError("upstream passage requires a manual conversational translation")
        text = text.replace(before, after, 1)
    return text.encode("utf-8")


def host_paths(kind):
    if kind == "codex":
        return "plugins/three-axes-framework", "plugins/three-axes-framework/skills/three-axes-framework/SKILL.md"
    if kind == "hermes":
        return "skills/three-axes-framework", "skills/three-axes-framework/SKILL.md"
    if kind == "claude":
        return "", ""
    raise ValueError("unknown host")


def check(root):
    lock = json.loads(local(root, STATE).read_text(encoding="utf-8"))
    version = release_version(dict(tag_name=lock["tag"], draft=False, prerelease=False, published_at=True))
    if version != lock["version"] or not re.fullmatch(r"[0-9a-f]{40}", lock["revision"]):
        raise ValueError("invalid release binding")
    if digest(local(root, BASE).read_bytes()) != lock["source_files"][SKILL]:
        raise ValueError("upstream merge baseline changed")
    for rel, sha in lock["managed_files"].items():
        if digest(local(root, rel).read_bytes()) != sha:
            raise ValueError(f"managed file drift: {rel}")
    kind = lock["host"]
    prefix, skill = host_paths(kind)
    if kind == "codex":
        manifest = json.loads(local(root, prefix + "/.codex-plugin/plugin.json").read_text(encoding="utf-8"))
        if manifest["name"] != "three-axes-framework" or manifest["version"] != version:
            raise ValueError("Codex manifest identity/version mismatch")
    elif kind == "hermes":
        if f"\nversion: {version}\n" not in local(root, skill).read_text(encoding="utf-8"):
            raise ValueError("Hermes version mismatch")
    else:
        catalog = json.loads(local(root, ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        entries = [p for p in catalog["plugins"] if p["name"] == "three-axes-framework"]
        if len(entries) != 1 or entries[0]["source"] != dict(source="github", repo=UPSTREAM, ref=lock["tag"], sha=lock["revision"]):
            raise ValueError("Claude marketplace release pin mismatch")
    if kind == "hermes":
        provenance = json.loads(local(root, "SOURCE.json").read_text(encoding="utf-8"))
        current = provenance["additional_sources"]["three-axes-framework"]
        if current != dict(repository="https://github.com/" + UPSTREAM, revision=lock["revision"], tag=lock["tag"], sha256=lock["source_files"]):
            raise ValueError("Hermes current provenance mismatch")
    return lock


def plan(root, release, revision, blobs):
    """Build every proposed byte before modifying any checkout file."""
    lock = check(root)
    version = release_version(release)
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("expected a full upstream commit")
    manifest = json.loads(blobs[MANIFEST])
    if manifest.get("name") != "three-axes-framework" or manifest.get("version") != version:
        raise ValueError("release tag and upstream manifest disagree")
    if version == lock["version"]:
        if revision != lock["revision"] or {p: digest(b) for p, b in blobs.items()} != lock["source_files"]:
            raise ValueError("published version was rewritten")
        return {}
    if tuple(map(int, version.split("."))) < tuple(map(int, lock["version"].split("."))):
        raise ValueError("refusing an upstream downgrade")
    if set(blobs) != set(lock["source_files"]):
        raise ValueError("upstream runtime layout changed; review host mapping manually")
    for path, data in blobs.items():
        if path.startswith("hooks/") and digest(data) != lock["source_files"][path]:
            raise ValueError("upstream hooks changed; review native/conversational adapters manually")
        if (path not in (SKILL, MANIFEST, "LICENSE", "CHANGELOG.md")
                and not path.startswith(("commands/", "hooks/"))
                and digest(data) != lock["source_files"][path]):
            raise ValueError("unmapped upstream runtime changed; review host adaptation manually")
    # Component paths/dependencies cannot silently change underneath an adapter.
    comparable = {k: v for k, v in manifest.items() if k != "version"}
    if comparable != lock["manifest_contract"]:
        raise ValueError("upstream manifest contract changed; review adapter manually")
    kind = lock["host"]
    prefix, skill = host_paths(kind)
    updates = {BASE: blobs[SKILL]}
    if kind == "claude":
        path = ".claude-plugin/marketplace.json"
        catalog = json.loads(local(root, path).read_text(encoding="utf-8"))
        entry = next(p for p in catalog["plugins"] if p["name"] == "three-axes-framework")
        entry["source"] = dict(source="github", repo=UPSTREAM, ref=release["tag_name"], sha=revision)
        updates[path] = encode(catalog)
    else:
        merger = update_conversational_skill if kind == "hermes" else merge_skill
        updates[skill] = merger(local(root, skill).read_bytes(), local(root, BASE).read_bytes(), blobs[SKILL])
        for path, data in blobs.items():
            if path.startswith("commands/"):
                updates[prefix + "/references/source-commands/" + path.removeprefix("commands/")] = data
        for path in ("LICENSE", "CHANGELOG.md"):
            updates[prefix + "/" + path] = blobs[path]
        if kind == "codex":
            path = prefix + "/.codex-plugin/plugin.json"
            adapter = json.loads(local(root, path).read_text(encoding="utf-8"))
            adapter["version"] = version
            updates[path] = encode(adapter)
        else:
            text, count = re.subn(r"^version: [^\n]+$", "version: " + version, updates[skill].decode("utf-8"), count=1, flags=re.M)
            if count != 1:
                raise ValueError("missing Hermes version")
            updates[skill] = text.encode("utf-8")
            updates[prefix + "/references/source-SKILL.md"] = blobs[SKILL]
            source = json.loads(local(root, "SOURCE.json").read_text(encoding="utf-8"))
            source.setdefault("additional_sources", {})["three-axes-framework"] = dict(
                repository="https://github.com/" + UPSTREAM, revision=revision,
                tag=release["tag_name"], sha256={p: digest(b) for p, b in blobs.items()})
            updates["SOURCE.json"] = encode(source)
    managed = dict(lock["managed_files"])
    for path, data in updates.items():
        if path not in (BASE, "SOURCE.json", ".claude-plugin/marketplace.json"):
            managed[path] = digest(data)
    lock.update(version=version, tag=release["tag_name"], revision=revision,
                source_files={p: digest(b) for p, b in blobs.items()}, managed_files=managed)
    updates[STATE] = encode(lock)
    # Append a reviewable log/changelog record; repeat runs are a true no-op.
    note = f"Synchronize Three Axes {version} from `{revision}` ({release['tag_name']}); preserve the {kind} host adapter."
    path = "CHANGELOG.md"
    changelog = local(root, path).read_text(encoding="utf-8")
    if "## [Unreleased]" not in changelog:
        raise ValueError("missing Unreleased changelog section")
    updates[path] = changelog.replace("## [Unreleased]", "## [Unreleased]\n\n### Changed\n\n- " + note, 1).encode("utf-8")
    path = "JOURNAL.md"
    journal = local(root, path).read_text(encoding="utf-8")
    entry = f"## Upstream synchronization — {version}\n\n- {note}\n- Generated from Git blobs; no upstream code executed. Full CI and human review required before merge. No release/tag or user installation changed.\n- Files: {STATE}, {BASE}, host package/catalog, CHANGELOG.md.\n\n"
    first, rest = journal.split("\n", 1)
    updates[path] = (first + "\n\n" + entry + rest.lstrip("\n")).encode("utf-8")
    for path in updates:
        local(root, path)
    return updates


def apply(root, updates):
    for rel, data in updates.items():
        path = local(root, rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="offline drift check")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.check:
        lock = check(root)
        print(f"{lock['host']}: {lock['version']} at {lock['revision']}; managed files match")
        return
    release = api_release()
    release_version(release)  # validate before passing a ref to Git
    with tempfile.TemporaryDirectory(prefix="three-axes-release-") as folder:
        repo = Path(folder)
        git(repo, "init", "--quiet")
        git(repo, "fetch", "--quiet", "--depth=1", f"https://github.com/{UPSTREAM}.git", "refs/tags/" + release["tag_name"])
        revision = git(repo, "rev-parse", "FETCH_HEAD^{commit}").decode().strip()
        updates = plan(root, release, revision, source_blobs(repo, revision))
    apply(root, updates)
    check(root)
    print("updated" if updates else "already synchronized")


if __name__ == "__main__":
    main()
