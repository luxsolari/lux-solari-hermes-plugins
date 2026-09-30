# Three Axes Hermes routes

Load `three-axes-framework`, then ask in ordinary chat: “three-axes setup”,
“three-axes status”, etc. These are assistant workflows, not registered slash
aliases or shell commands. Retained `source-commands/` files specify validation,
confirmation, merge-before-write, and one-question-at-a-time safeguards only;
do not execute their host-specific paths or hooks.

| Request | Behavior |
| --- | --- |
| three-axes / three-axes-framework | Show status, routes, and mode-switch signals. |
| three-axes setup | Ask scope and all three axes sequentially; save the confirmed persistent profile using Hermes file tools. |
| three-axes status | Resolve defaults → global → project → session and report each effective value's source. |
| three-axes mode PRESET | Replace the full session override in conversation with the preset below. |
| three-axes set AXIS=VALUE [--project\|--global] | Validate then merge the named axis into project/global state; without a scope flag, change only conversation state. Read before writing. |
| three-axes audit [what went wrong] | No writes/new code. Quote the violation, name IR ID, mechanical cause, proposed correction, and CLEAN/DEGRADED/COMPROMISED rating; then stop. |
| three-axes handoff [output-path] | State, failures, decisions, open questions. Write only to a requested path; otherwise print. |
| three-axes log [note] | Read JOURNAL.md, add newest-first entry at repository root; compact past ~40 entries without dropping decisions/failures. Do not invent verification. |

Global profile: `three-axes-profile.json` under `HERMES_HOME` (fallback
`~/.hermes`). Project profile: `.three-axes.json`. Session overrides and scoped
signals: conversation only. Do not read/write legacy Codex or Claude global
state unless the user explicitly requests migration. Unknown/invalid axis values
must be reported rather than silently coerced. Setup requires a nonempty valid
persistent JSON object; valid partial profiles inherit omitted values.

| Preset | mastery | consequence | intent |
| --- | --- | --- | --- |
| learning | low | low | growth |
| output | high | medium | output |
| production | high | high | output |
| explore | low | medium | growth |
| balanced | medium | medium | balanced |

Task signals retain their durations in SKILL.md and never suspend the Integrity
Rules. No SessionStart, tool-denial gate, profile writer hook, or automatic
session-file clearing is implemented by this port.
