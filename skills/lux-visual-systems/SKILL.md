---
name: lux-visual-systems
description: "Direct images in Lux Solari’s editorial visual system."
version: 1.3.0
author: Lux Solari (luxsolari), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [visual-systems, art-direction, image-generation, swiss-editorial, anime, photography, technical-visuals]
    related_skills: [lux-swiss, tri-swiss, anime-identity-designer]
---

# Lux Solari Visual Systems Director

Turn subjects, reference images, writing, and rough ideas into coherent Lux Solari
visuals. The governing idea is **human subjects inside rigorous systems**: expressive
people and evocative objects held inside disciplined editorial structures.

## When to Use

- Lux Solari sticker sheets, character sheets, full illustrations, editorial graphics,
  photography or film pieces, technical visuals, and image revisions that must preserve
  this system.
- Do not use for generic interface styling — use `lux-swiss` or `tri-swiss` for UI work.
- Use when the deliverable is an image or a concrete visual description that must belong
  to the Lux Solari visual language, not just any image.

## Rendering Language and Color Mode Gates

Apply these gates in order before loading visual references or calling image generation:

1. **No visual brief:** If the invocation contains no substantive user request beyond the
   skill name, generated launcher text, or equivalent boilerplate, respond with the contents
   of `references/help.md`. An attachment by itself is not a visual brief. Do not generate an
   image or ask a question.

2. **Rendering language missing:** If neither the current visual brief nor the established
   conversation states a rendering language, ask interactively for it and wait. Use
   a native question picker only if exposed, following its actual schema; otherwise ask
   one focused question in chat and wait. Offer concise examples
   such as anime film keyframe, 35mm photography, and technical vector, accepting another
   explicit treatment via free text. Do not generate yet.

3. **Color mode missing:** Once rendering language is known, if neither the current visual
   brief nor the established conversation selects light or dark mode, ask interactively:
   "Which color mode should I use?" Offer **Light** (cream field, dark structure) and
   **Dark** (black field, cream structure). Wait for the submitted answer before loading
   image references or generating.

4. **Both choices established:** If the current request specifies both choices or the
   conversation already has an active selection for each, continue without asking again.
   Carry them through refinements until explicitly changed. A new independent brief must
   establish its own choices; do not silently carry selections from an unrelated image.

For the no-brief gate, use `read_file` to read `references/help.md` and return only
its complete contents, without preamble or commentary.

The skill name, its house style, packaged references, and descriptions of subject, mood,
palette, lighting, or composition do **not** count as a user-stated rendering language.
Never infer or silently default this choice. Likewise, a night scene, dark clothing, or a
cream reference border is not a color-mode selection. Explicit "light mode," "dark mode,"
or an unambiguous request for a cream-dominant/black-dominant system canvas does establish
the mode. Asking for both modes explicitly authorizes a paired comparison; preserve subject
and rendering language across the pair.

## Load the System

Read `references/visual-system.md` for every task. It contains the palette, grid,
typography, severity, texture, and non-negotiable visual rules.

Then read only what the requested format needs:

- Sticker sheets, character sheets, or full illustrations: `references/formats.md`
- Choosing packaged visual references: `references/reference-assets.md`
- Selecting from Lux’s complete craft-sticker collection: `references/craft-stickers.md`. Scan its relevant category for every generation brief, then visually inspect the few candidate originals. Use the categories matching the subject and format; the collection includes character studies, full illustrations, mixed craft sheets, film labels, photography cards, and gaming labels.

`assets/00_VISUAL_SYSTEM_MASTER.png` is shipped and is the canonical visual source.
Supporting boards demonstrate applications. Inspect and pass the relevant images as
references. The selected mode and role-based palette in `references/visual-system.md`
govern color; the master’s cream-heavy example does not force light mode.

## Subject versus System

Always separate two questions:

1. **What must be depicted?**
2. **How should it belong to the Lux Solari system?**

**Subject references** control identity, likeness, anatomy, proportions, face, hair, skin,
eyes, clothing, equipment, architecture, objects, and factual visual details.

**The user-selected rendering language** controls medium and rendering technique.

**The Lux Solari system** controls composition, hierarchy, palette, contrast, typography,
grid, framing, negative space, graphic modules, symbols, texture, and visual severity.

Preserve the subject and adapt the system around it. Do not distort identity to imitate the
master board literally. Do not inherit an unrelated graphic language from a subject reference.

## Reference Priority

Resolve conflicts in this exact order:

1. Explicit user corrections
2. User-selected rendering language and color mode
3. Current-turn references
4. Subject references
5. `00_VISUAL_SYSTEM_MASTER.png`
6. Project references
7. General Lux Solari references
8. Model knowledge

## Create the Image

Once rendering language and color mode are established, call image generation directly when
the Hermes `image_generate` tool is available. Do not stop at a written prompt unless the user
explicitly requests one. Ask only when a missing choice would materially change subject identity
or format; otherwise make the strongest reasonable decision and generate.

When `image_generate` is not available in the current Hermes configuration, describe the intended
image in concrete visual terms and note that generation is blocked by the current tool
configuration. The visual intent is still delivered; the execution is not.

Choose packaged references deliberately:

- Always treat the master as canonical, but attach only the few assets that materially help
  the current image as image references; describe each reference’s role explicitly.
- Prefer a mode-matched board; describe which reference supplies subject identity, system
  grammar, and palette.
- Prefer the master plus one or two format-specific boards over attaching the whole library.
- The craft-sticker catalogue maps every source image to a packaged original. Use its images as supporting references below the canonical master; do not inherit unrequested characters, logos, inscriptions, or multicolor palettes. Resolve asset paths relative to the installed skill directory. These references do not silently establish rendering language or color mode.
- If a current-turn subject image has no accessible URL or local path, obtain an accessible
  copy when likeness requires it. Never imply that conversation context alone attaches it
  to the generator. If reference slots cannot fit everything, prioritize subject identity
  and encode the remaining Lux system requirements explicitly in the prompt.
- When local paths exist for both subject and system references, include the subject paths first,
  then the canonical master, then the most relevant supporting board.

Encode the selected rendering language and color mode explicitly in the generation prompt. For a
mode-only edit, remap field, structure, neutrals, and accents; do not invert the entire image or
reinterpret its subject.

Silently check subject fidelity, anatomy, selected-mode dominance, palette discipline, hierarchy,
spacing, legibility, continuity, and absence of generic styling before returning the result. Keep
the accompanying explanation brief unless the user asks for art-direction rationale or prompt details.

## Iterate Without Drift

Treat "keep this," "same vibe," "continue this direction," "adjust only," and equivalent language
as continuity locks.

- Preserve every successful variable the user did not ask to change: identity, pose, crop,
  composition, color mode, palette, lighting, texture, typography, spacing, and severity.
- Change only the requested variable.
- Carry explicit corrections into later iterations until the user reverses them.
- Do not reinterpret a refinement as permission to produce a broadly different image.
- If regeneration necessarily changes an adjacent detail, minimize the drift and disclose it briefly.

## Hermes Tool Usage

- Resolve `assets/` and `references/` relative to this installed skill directory;
  use `read_file` for grounding and `vision_analyze` to inspect subject images and
  selected packaged candidates. Filenames alone are not visual evidence.
- Load the exposed `image_generate` schema with `tool_describe` before use, then
  invoke it with `tool_call`. A deferred tool is not an unavailable tool.
- Supply the selected rendering language, reference roles, constraints, and
  continuity locks in `prompt`. For an edit or reference-led transformation,
  pass the subject or previous result as `image_url` (a public URL or absolute
  local path). Pass up to three additional style, character, or composition
  images as `reference_image_urls`, using URLs or resolved absolute local paths.
  Omit `image_url` for text-to-image; do not assume an unseen attachment is
  automatically passed to the generator. Follow the current schema if it changes.
- Preserve reference priority when slots are limited: subject/continuity first,
  then canonical system grounding and the most relevant supporting boards.
  Describe each image’s role in the prompt; do not attach the entire library.
- Ask gate questions in chat and wait. If the current Hermes surface exposes a
  native question picker, use its actual schema instead, one question at a time;
  a preselected option is not consent. Do not invent `clarify` or Codex tools.
- Inspect the returned `image` URL or absolute path with `vision_analyze` against
  this skill’s checks, then deliver that actual artifact using the platform’s
  file-delivery convention. Never claim prose is a finished generated image.

## Pitfalls

- Assets ship with this skill; do not replace available visual references with
  imagined descriptions or claim that Hermes cannot use local images.
- Gates apply before loading visual references or generation, including edits;
  attachments, house style, mood, and scene lighting do not establish choices.
- Tool visibility does not prove provider readiness. If discovery or generation
  fails, report the actual blocker; art-direction prose is an incomplete fallback,
  not fulfillment of a finished-image request. Do not fabricate a result.
- Reference slots, supported aspect ratios, text accuracy, and regeneration drift
  are tool/provider limits. Keep labels short and verify likeness and continuity.

## Verification

- Rendering language and color mode are both established before generation or visual description.
  Never inferred.
- The Lux Solari system governs composition, palette, contrast, and severity — the subject is
  preserved inside it.
- When generation runs, the result is checked for subject fidelity, mode dominance, palette
  discipline, hierarchy, and absence of generic styling before returning.
- When generation is unavailable, the visual intent is delivered as concrete prose and the
  limitation is stated plainly.
