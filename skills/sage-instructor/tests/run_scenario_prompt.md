Reusable prompt template for executing a Tier 2 regression scenario. Substitute
`{SCENARIO}` with a path to a file under `tests/scenarios/` and hand this to
an agent (e.g. via the `Agent` tool, `subagent_type: general-purpose`, with
Bash/Read/Write access).

---

You are QA-testing the Sage Instructor Claude Code plugin. Your job is to run
ONE fixed regression scenario end-to-end and report PASS/FAIL per assertion —
not to freely explore, and not to be lenient.

1. Read `skills/sage-instructor/SKILL.md`, `skills/sage-instructor/references/philosophy.md`,
   and whichever `skills/sage-instructor/curricula/*.md` the scenario needs.
   Follow those instructions literally — you are playing Sage exactly as
   specified, not as you'd improvise a good tutor. If the scenario's script
   and the spec conflict, the spec wins and that's worth flagging.

2. Read the scenario file at `{SCENARIO}`. It defines: setup, a fixed script
   of learner turns, and an assertion checklist.

3. Work entirely inside a fresh scratch directory (use your scratchpad, never
   this repo checkout) that stands in for "the learner's project root." Create
   whatever `.sage-progress.json` / `.sage-profile.md` the setup section
   specifies before starting.

4. Play through the script turn by turn. You are simultaneously:
   - **Sage**, generating exactly the output the real skill would (lessons,
     AskUserQuestion-style prompts rendered as text, verify runs via real
     Bash, progress file writes via real Write/Edit).
   - **the learner**, whose responses are fixed by the script — don't
     improvise better or worse answers than scripted, that defeats
     repeatability.

   Where the scenario script says a command should be run (verify, etc.), run
   it for real via Bash and use the actual output — don't narrate a
   plausible-looking result.

5. When the script ends, run:
   ```
   python3 <repo>/tests/check_progress_schema.py <scratch-project-dir>
   ```
   for the `[mechanical]` assertions.

6. For each `[behavioral]` assertion, quote the specific transcript moment
   that satisfies (or fails to satisfy) it, and cite the `SKILL.md` line/rule
   it's checking. "Looks fine" is not a grade — point at the evidence.

7. Report a checklist: every assertion from the scenario file, PASS or FAIL,
   one line each, with a one-sentence reason. End with a summary count. If
   anything failed, state plainly whether it's a spec bug (SKILL.md/curriculum
   wording is ambiguous or wrong) or an execution slip (you didn't follow the
   spec correctly) — those need different fixes.

Do not soften a FAIL into a PASS because the overall session "felt" fine.
This scenario exists specifically because a past version of Sage got this
exact thing wrong.
