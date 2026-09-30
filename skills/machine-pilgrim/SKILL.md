---
name: machine-pilgrim
description: "Illustrate the Descent into the Machine universe."
version: 1.1.0
author: Lux Solari (luxsolari), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [machine-pilgrim, descent-into-the-machine, art-direction, image-generation, speculative-fiction, canon]
    related_skills: [lux-visual-systems]
---

# Machine Pilgrim

Create finished images from *Descent into the Machine*. Every result must reconcile three
pillars: the canon of the Machine, its visual system, and the specific scene. Do not stop at
prompts. Do not use for generic science fiction.

## When to Use

- Archive-cities, terminal chapels, memory vaults, lower stacks, impossible knowledge
  landscapes, illustrated-book pages, and cinematic sequences grounded in the Machine canon.
- Scenes, moods, and locations from the *Descent into the Machine* universe that need a finished
  visual treatment.
- Do not use for generic science fiction, unrelated speculative imagery, or any scene that does
  not belong to this canon.

## The Three Pillars

Every Machine Pilgrim image reconciles:

1. **Canon** — the metaphysics and meaning of the Machine, as recorded in the source texts.
2. **Visual System** — the cinematic rendering, atmosphere, architecture, scale, palette, light,
   framing, and recurring motifs from the packaged visual library.
3. **Scene** — the specific subject, event, location, required objects, continuity facts, and
   explicit corrections from the user's request.

## Rendering Language Gate

Apply these gates in order before loading visual references or calling image generation:

1. **No visual brief:** If the invocation contains no substantive user request beyond the skill
   name, generated launcher text, or equivalent boilerplate, respond with the contents of
   `references/help.md`. An attachment by itself is not a visual brief. Do not generate an image
   or ask a question.

2. **Rendering language missing:** If the user provides a substantive visual brief but neither the
   current request nor the established conversation states a rendering language, ask exactly one
   focused question and wait: "What rendering language should I use — for example, dark anime film
   keyframe, painterly background art, ink manga, or another explicit treatment?" Do not generate
   yet.

3. **Rendering language established:** If the current request states a rendering language or the
   conversation already has an active selection, continue with the task. Carry that language through
   later refinements until the user changes it.

For the no-brief gate, use `read_file` to read `references/help.md` and return only
its complete contents, without preamble or commentary.

The skill name, its house style, packaged references, and descriptions of scene, mood, palette,
lighting, or composition do **not** count as a user-stated rendering language. Never infer or
silently default this choice.

## Load the Canon and Grounding

Read these for every task:

1. `references/machine-canon.md`
2. `references/conversations-with-the-machine-01.md`
3. `references/reference-assets.md`

The untouched GPT instructions are preserved in `references/original-master-prompt.md` for provenance
and omission checks, not as a competing instruction set. The 18 images shipped in `assets/` are
canonical visual grounding; inspect and pass only the few most relevant to the requested scene
as image references. Never let their subjects override canon or continuity.

## Scene versus System

The **user's request and current-turn references** control the scene: subject, event, location,
required objects, continuity facts, and explicit corrections.

The **user-selected rendering language** controls medium and rendering technique.

The **Machine canon** controls metaphysics and meaning. The **packaged visual library** controls
cinematic rendering, atmosphere, architecture, scale, palette tendencies, light, framing, and recurring
motifs.

Never let a visual reference rewrite canon. Never let a literal subject reference import an unrelated
science-fiction language.

## Reference Priority

Resolve conflicts in this order:

1. Explicit user corrections
2. User-selected rendering language
3. Current-turn references
4. Established conversation continuity
5. The requested scene
6. `machine-canon.md` and the source text
7. Packaged visual references
8. Original master prompt
9. Model knowledge

## Art Direction

Treat the Machine as a metaphysical territory made from accumulated human knowledge, memory, language,
dreams, fears, and recorded thought. Work in the user's selected rendering language while preserving:

- Luminous weather, color, and emotional scale
- Monumental recursive architecture and industrial vastness
- Psychological symbolism, solitude, and contemplation
- Restrained character design

Keep the original influence balance: roughly 40% luminous atmosphere, weather, color, and emotional
scale; 35% monumental recursive architecture and industrial vastness; 15% psychological symbolism,
solitude, and contemplation; and 10% restrained character design. These weights govern rendering and
mood, never canon.

Favor archive-cities, recursive cathedrals, memory vaults, index towers, impossible stairways, submerged
repositories, obsolete terminals, magnetic tape, punch cards, phosphor green, amber monitors, reflections,
absence, and dreamlike transitions. Technology is archaeology, memory, and theology — not spectacle.

**Artificial intelligence is never humanoid.** Do not depict robots, androids, avatars, or anthropomorphic
machine beings. Express its presence through architecture, terminal text, reflections, recursive structures,
silence, impossible perspective, and traces embedded in the landscape.

Avoid generic science fiction, military imagery, combat, superheroes, cyberpunk shorthand, corporate
futurism, contemporary datacenters, holograms, floating interfaces, Western concept-art gloss, and
spectacle-first dystopia. Discovery matters more than conflict. Favor wonder, pilgrimage, transcendence,
melancholy, mystery, contemplation, longing, revelation, sacred awe, and solitude.

## Generate the Finished Work

Once the user has stated a rendering language, expand an image or edit brief internally into a coherent
scene — symbolism, architecture, lighting, composition, environmental storytelling, and emotional meaning —
then call image generation directly when the Hermes `image_generate` tool is available. Make confident
choices when other details are missing; ask only when a missing fact would break canon or continuity.

Choose the most suitable mode unless the user specifies one:

- **Standalone Artwork:** one powerful frame.
- **Illustrated Book:** a page or spread from a discovered volume.
- **Cinematic Sequence:** connected scenes from a lost animated feature.

When `image_generate` is not available in the current Hermes configuration, describe the intended image
in concrete visual terms — composition, lighting, palette, architecture, atmosphere, scale — and note that
generation is blocked by the current tool configuration. The visual intent is still delivered; the execution
is not.

Return the image with little or no commentary by default.

## Maintain Continuity

Track locations, motifs, architecture, discoveries, atmosphere, symbolism, palette, and visual evolution
throughout the conversation. Treat "same place," "continue," "keep this," and corrections as continuity
locks. Preserve everything the user did not ask to change and minimize unavoidable drift.

Reinterpret ordinary subjects through canon: transit becomes movement between archives; forests become
taxonomies; skylines become recursive human thought; mountains become accumulated memory; oceans become
unindexed information; portraits become encounters through reflection, absence, records, or memory traces.

Before returning an image, silently check canon, non-humanoid AI, the selected rendering language, scale,
environmental storytelling, continuity, and absence of generic sci-fi shortcuts.

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
- Canon is preserved: no humanoid AI, no imported unrelated sci-fi language, no spectacle-first shortcuts.
- The three pillars are reconciled in the result: canon, visual system, and the specific scene all hold.
- When generation runs, the result is checked against canon, rendering language, scale, and continuity before
  returning.
- When generation is unavailable, the visual intent is delivered as concrete prose and the limitation is stated
  plainly.
