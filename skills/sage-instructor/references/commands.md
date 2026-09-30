# Sage Hermes routes

Load `sage-instructor` with `skill_view`, or invoke the installed skill by name,
then ask in ordinary chat using one of these routes:

`sage start` · `sage next` · `sage lesson` · `sage challenge` · `sage checkpoint` ·
`sage progress` · `sage drill` · `sage review` · `sage hint` · `sage explain` ·
`sage stuck` · `sage recap` · `sage status` · `sage help` · `sage reset` ·
`sage phase` · `sage tracks` · `sage switch` · `sage new-track` · `sage exercise`.

These are conversational workflows, not registered `/sage-*` aliases. Bare
`/status`, `/help`, and `/reset` belong to Hermes itself and may be intercepted;
use “sage status”, “sage help”, or “sage reset” instead. Original command files
are retained in `source-commands/` for provenance. Preserve their confirmation
gates, progress transitions, diagnosis, and source recording, but substitute
Hermes tools and project-local state paths for host-specific instructions.

Bundled curricula are in this skill's `curricula/`; custom curricula belong in
the learner project's `curricula/`. Prefer project curricula with the same ID,
then fall back to the bundled track. Learner-generated profiles and progress
remain at project root. Use plain-chat choices if no question tool is available.
