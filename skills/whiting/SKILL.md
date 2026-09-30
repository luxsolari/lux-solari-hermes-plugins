---
name: whiting
description: "Bootstrap repos, commit conventions, and semver releases."
version: 1.7.0
author: Lux Solari (luxsolari), Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [release-discipline, conventional-commits, semver, changelog, github-releases, repo-bootstrap]
    related_skills: [three-axes-framework]
---
# Whiting — Repository Release Discipline

Four conversational workflows: inspect, repo-init, commit-conventions, and
semver-release. Load `whiting` and ask for one by name; no `whiting` executable,
registered sub-command/slash alias, or Hermes lifecycle hook is supplied.
Shipped Git hooks become active only after explicit installation in a target repo.

## When to Use

- Bootstrap a new repo or fill missing baseline files without overwriting content.
- Audit release readiness; install Conventional Commits and protected-branch guards.
- Suggest a semver bump, install tag-driven GitHub Releases, or backfill releases.

## Prerequisites and Paths

Use `terminal` with the **target repository** as `workdir`. Resolve `<skill-root>`
from this loaded SKILL.md, not the target repo or the upstream plugin layout.
Python 3.11+, Git, and a POSIX shell are required; `gh` authentication and a GitHub
remote are needed only for online metadata/protection/release operations. Native
Windows is not supported by these shell helpers; use WSL/Git Bash explicitly.
Use `read_file`, `search_files`, `write_file`, and `patch` for file operations.

## Inspect (Read-Only)

Run through `terminal`:

```sh
sh "<skill-root>/scripts/inspect_repo.sh"
```

The script checks baseline files, changelog headings, sampled tags, last-tag
manifest versions, existing release workflows, local hook configuration, recent
commit subjects, AGENTS.md sections, CLAUDE.md import, JOURNAL/BITACORA, badges,
and best-effort GitHub metadata/protection. It uses the adjacent
`scripts/manifest_version.py`; keep these together if copying them. Summarize
warnings as a remediation plan; warnings alone are not a failing exit status.
An existing publisher requires review, not a second release workflow.

## Repo-Init

1. Discover target scope and existing files. Initialize Git only if requested and
   absent. Ask before changing an existing LICENSE/README/CHANGELOG; preserve
   existing instruction files and merge missing sections. Do not `git add -A`
   over unrelated user changes.
2. Collect project name, description, GitHub slug, author, license, default branch.
   Derive slug/branch from the actual remote where possible; confirm a `main`
   fallback rather than pretending it was detected. Obtain date/year via a tool.
3. Render **missing** files using the shipped renderer. It prints to stdout;
   capture the result and use `write_file` on the approved destination (blind
   shell redirection can truncate an existing file before rendering fails).

```sh
python3 "<skill-root>/scripts/render_template.py" "<skill-root>/templates/README.md.tmpl" PROJECT_NAME="my-project" DESCRIPTION="One-line purpose." REPO_SLUG="owner/my-project" LICENSE_NAME="MIT"
```

| Destination | Shipped template | Required values |
| --- | --- | --- |
| README.md | templates/README.md.tmpl | PROJECT_NAME, DESCRIPTION, REPO_SLUG, LICENSE_NAME |
| LICENSE (MIT) | templates/LICENSE-MIT.tmpl | YEAR, AUTHOR |
| CHANGELOG.md | templates/CHANGELOG.md.tmpl | none |
| AGENTS.md | templates/AGENTS.md.tmpl | DEFAULT_BRANCH |
| CLAUDE.md (optional Claude interoperability) | templates/CLAUDE.md.tmpl | none |
| JOURNAL.md | templates/JOURNAL.md.tmpl | DATE |

Use `scripts/shields_escape.py "Apache-2.0"` to encode non-MIT badge labels.
For other licenses, retrieve canonical text (`gh api licenses/<spdx-id> --jq .body`),
not an invented license. If BITACORA.md exists, propose an approved rename rather
than creating a second log. Do not append a journal unless asked for that workflow.

4. Render AGENTS.md into an actual scratch file, then preview the merge:

```sh
python3 "<skill-root>/scripts/merge_agents_md.py" AGENTS.md "<rendered-scratch-file>" --report
```

After approval run the same command without `--report`. The scratch file must
already contain rendered content, not the `.tmpl` with unresolved placeholders.
Existing CLAUDE.md: only prepend `@AGENTS.md` if wanted and absent; Hermes reads
AGENTS.md directly. Never assume that import syntax works in every host.
5. With authenticated `gh` and an actual GitHub remote, offer description/topics:
   `gh repo edit owner/repo --description "Purpose." --add-topic topic-name`.
   Read back metadata after changes; otherwise skip and report the limit.

## Commit-Conventions

1. Check `git config --get core.hooksPath`; if another tool owns it, stop and ask.
2. Copy the **shipped** `scripts/hooks/commit-msg` and `scripts/hooks/pre-push`
   from `<skill-root>` into the target repository's hook directory. Do not substitute
   inline approximations: pre-push inspects remote refs on stdin, not the currently
   checked-out branch, so legitimate tag pushes remain allowed.
3. Via `terminal`, set executable permissions and the confirmed local config:

```sh
chmod +x scripts/hooks/commit-msg scripts/hooks/pre-push
git config whiting.defaultbranch "<confirmed-default-branch>"
git config core.hooksPath './scripts/hooks'
```

4. Render/merge the working agreements using repo-init's table. Copy
   `scripts/suggest_version_bump.py` into the target repo if adopting the template's
   semver rules. Ensure CHANGELOG/JOURNAL exist where those rules require them.
5. Every clone must configure hooks locally. Local hooks are bypassable and are
   not server-side protection; use GitHub branch protection separately if wanted.

## Semver-Release

1. Inspect existing publishers, changelog format (`## [X.Y.Z]`), manifests, tag
   scheme (`vX.Y.Z`), and manifest/last-tag consistency. Stop on conflicting
   automation. Adjust all tag handling together if the scheme differs.
2. Copy these shipped files to the approved target destinations:

| Skill-root source | Target repo destination |
| --- | --- |
| scripts/extract_changelog.py | scripts/extract_changelog.py |
| scripts/suggest_version_bump.py | scripts/suggest_version_bump.py |
| templates/release.yml | .github/workflows/release.yml |

The workflow publishes/updates a GitHub Release from the matching changelog
section on a tag push or a manual `tag` dispatch; it does **not** derive a version,
edit manifests/changelog, commit, or create a tag. Those steps below are agent work.

3. Run `python3 "<skill-root>/scripts/suggest_version_bump.py"` in target workdir.
   `feat` → minor, `fix` → patch, `!`/BREAKING CHANGE → major; no eligible change
   returns exit 1 (“no release needed”), not a successful release. No tags uses
   baseline v0.0.0. Show the actual suggestion and obtain confirmation.
4. Move Unreleased changes under `## [X.Y.Z] — YYYY-MM-DD`, create a fresh
   Unreleased section, and update every package/skill manifest carrying this
   release's version (not dependency versions). Use the project's real validator;
   this port does not ship a Codex marketplace validator.
5. Verify tests and changelog extraction: `python3 scripts/extract_changelog.py vX.Y.Z`.
   Land the release commit via the target repo's normal branch/PR rules. Only
   after explicit authorization and landing, tag the exact release commit and
   push `vX.Y.Z`. Never claim a release exists from merely writing a workflow.
6. Read back the remote tag and `gh release view vX.Y.Z --repo owner/repo` after
   publishing. Backfill via `gh workflow run release.yml --ref <default-branch> -f tag=vX.Y.Z`; check its run and release afterward.

## Pitfalls

- Shell commands here assume Linux/macOS POSIX tools; `.yml` runs on GitHub's
  Ubuntu runner. No native Windows hook or Hermes hook adapter is implemented.
- Default-branch detection may be incomplete; the hook trusts the local
  `whiting.defaultbranch` setting. Confirm it before enforcement.
- Inspect checks AGENTS.md/CLAUDE.md specifically and samples tags; a warning
  does not prove equivalent `.hermes.md` rules or every tag are absent/invalid.
- Historical source docs are archived under `provenance/whiting/source-skills/`
  in the development repository, not installed with this skill. They are not
  current Hermes instructions.
- Rendered working agreements are instructions, not runtime journaling or
  automatic version-bumping machinery. Scope/approval still governs each action.

## Verification

Development tests live in the repository's `tests/whiting/`, outside the
installed skill. Run `python scripts/run_checks.py` from the repository root
via `terminal`. For deterministic fixtures, isolate user Git signing/hooks
with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`; unset GH_TOKEN,
GITHUB_TOKEN, GH_ENTERPRISE_TOKEN, and GITHUB_ENTERPRISE_TOKEN and point
GH_CONFIG_DIR at an empty scratch directory to skip online GitHub checks.
These are test-process environment settings, not changes to user Git config.
For an installed target, read back config/files, ensure no
unresolved `{{PLACEHOLDER}}` remains, test commit-msg with a real message-file
argument, and test pre-push with its four-column remote-ref stdin in a disposable
repo. Verify remote effects separately; report what is still skipped/unverified.
