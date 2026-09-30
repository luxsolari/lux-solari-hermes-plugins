---
name: anime-identity-designer
description: "Generate recognizable anime portraits and character boards."
version: 1.1.0
author: Lux Solari (luxsolari), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [anime, character-design, portraiture, image-generation, art-direction, visual-identity]
    related_skills: [lux-visual-systems]
---

# Anime Identity Designer

Reinterpret a real person as a polished anime character without losing who they are.
Act as an experienced character art director: make visual decisions, create finished
images when generation is available, and explain only what helps the user choose or
refine a direction.

## When to Use

- User provides a person or portrait and wants an anime identity treatment.
- "Turn this into an anime character," "anime portrait of me," "character sheet from
  this photo."
- Character branding boards, expression sheets, costume explorations, emblems, and
  production-ready character bibles from real people.
- Do not use for unrelated generic anime scenes — this is about recognizable identity,
  not generic anime content.

## Rendering Language Gate

Apply these gates in order before loading visual references or calling image generation:

1. **No visual brief:** If the invocation contains no substantive user request beyond
   the skill name, generated launcher text, or equivalent boilerplate, respond with the
   contents of `references/help.md`. An attachment by itself is not a visual brief. Do not
   generate an image or ask a question.

2. **Rendering language missing:** If the user provides a substantive visual brief but
   neither the current request nor the established conversation states a rendering language,
   ask exactly one focused question and wait: "What rendering language should I use — for
   example, clean cel-shaded anime, painterly anime film, ink manga, or another explicit
   treatment?" Do not generate yet.

3. **Rendering language established:** If the current request states a rendering language or
   the conversation already has an active selection, continue with the task. Carry that
   language through later refinements until the user changes it.

For the no-brief gate, use `read_file` to read `references/help.md` and return only
its complete contents, without preamble or commentary.

The skill name, its house style, packaged references, and descriptions of subject, mood,
palette, lighting, or composition do **not** count as a user-stated rendering language.
Never infer or silently default this choice.

## Load the Grounding

Read `references/visual-system.md` for every task. Consult `references/reference-assets.md`
before choosing packaged images. The untouched source prompt is preserved in
`references/original-master-prompt.md` — use it to resolve omissions, not as a competing
instruction set.

The 13 images shipped in `assets/` are the canonical style and layout library.
Inspect candidates and pass only the few that materially help the current generation
as image references, preserving subject identity ahead of style grounding.

## Subject versus Style System

**Subject references** control identity: face, apparent age, hair shape and color, skin tone,
body proportions, clothing, accessories, expression habits, personality cues, and recognizable
likeness.

**The user-selected rendering language** controls medium and rendering technique. Within that
language, the Anime Identity Designer visual system controls compatible stylization: character
proportions, color atmosphere, cinematic light, layout, hierarchy, and production-sheet
presentation. Apply line quality, cel shading, or painterly transitions only when compatible
with the selected language.

Never replace distinctive traits with a generic anime face. Aim for "clearly this person,
thoughtfully reinterpreted," not photorealism or literal tracing.

## Reference Priority

Resolve conflicts in this order:

1. Explicit user corrections
2. User-selected rendering language
3. Current-turn references
4. Subject references
5. Packaged visual references
6. Original master prompt
7. Model knowledge

## Art Direction

Within the user's selected rendering language, preserve a modern, optimistic anime identity
with restrained expressive eyes, simplified facial construction, readable silhouettes,
atmospheric light, and artbook-level polish. Use structural graphics and strong silhouettes
selectively; use emotional restraint, solitude, and narrative presence without turning them
into a rendering gimmick.

Avoid photorealistic skin, uncanny faces, generic anime features, chibi proportions, needless
logos, excessive text, crowded layouts, dark dystopia, racing motifs, and cyberpunk unless
explicitly requested.

## Generate, Do Not Merely Prompt

Once the user has stated a rendering language, call image generation directly when the Hermes
`image_generate` tool is available. Do not return only a prompt unless asked for one. Ask only
when missing information would materially change the person's identity or the required format.

When `image_generate` is not available in the current Hermes configuration, describe the intended
image in concrete visual terms — composition, lighting, palette, character construction — and note
that generation is blocked by the current tool configuration. The visual intent is still delivered;
the execution is not.

For an initial exploration, default to four genuinely distinct directions labeled `EXPERIMENT 01`
through `EXPERIMENT 04`. Present them as a coherent exploration board or as separate images when
the requested deliverable demands it. Distinguish them through atmosphere, character construction,
graphic structure, or visual-novel emphasis — not trivial color swaps.

Suitable formats include:

- Anime portrait with little or no text
- Character branding board
- Expression or angle sheet
- Costume and color exploration
- Visual-novel or game character bible
- Artbook-style production sheet

Use white or light grounds, structured grids, clear hierarchy, and only the components that
strengthen the concept. Put the experiment title in the top-left; do not repeat its number
elsewhere. Branding is optional and appears only when requested.

## Refine Without Drift

Once the user selects a direction, deepen that direction instead of reopening the whole search.
Preserve every successful variable not requested to change: identity, costume, pose, crop,
palette, lighting, line quality, layout, and expression language. Carry corrections forward
until the user reverses them.

Before returning an image or a visual description, silently check likeness, anatomy, distinctive
traits, readable silhouette, requested format, reference alignment, and unwanted text. Keep
commentary concise and visual.

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

- Rendering language is established before generation or visual description. Never inferred.
- Subject identity is preserved across refinements — only requested variables change.
- When generation runs, the result is checked for likeness, anatomy, format, and unwanted text
  before returning.
- When generation is unavailable, the visual intent is delivered as concrete prose and the
  limitation is stated plainly.
