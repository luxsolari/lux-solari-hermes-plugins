---
description: "Revisit a covered topic — usage: /sage-review pointers"
---
Read the Sage instructor skill at `.claude/skills/sage-instructor/SKILL.md` and execute the `/review` command with topic: $ARGUMENTS. Load context. If no topic argument was given, pull from `review_due` in the progress file instead — review the first entry (or let the learner pick if there are several). Give a condensed refresher on the topic (1-2 paragraphs covering concept + bridge + gotchas), followed by a small exercise to confirm retention. On success, remove the topic from `review_due` and bump its `topic_confidence` to `solid`.
