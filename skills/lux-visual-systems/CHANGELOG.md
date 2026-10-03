# Changelog

All notable changes to `lux-visual-systems` are documented in this file.

## [Unreleased]

## [1.3.0] — 2026-10-03

- Incorporate all 57 supplied Craft-stickers source images (56 distinct images), preserving original PNG bytes and mapping 13 source files to existing packaged boards to avoid redundant copies.
- Add 44 originals plus a subject/format catalogue and a source-to-package hash inventory so generation can select relevant references without access to the personal vault.
- Require inspection of relevant originals and preserve canonical-master, subject, rendering-language and color-mode precedence; film and gaming examples do not silently introduce their brands, text or palettes into unrelated images.

## [1.2.1] — 2026-09-11

- Show all four original custom GPT conversation starters in the plugin preview.

## [1.2.0] — 2026-09-11

- Add explicit light/dark palette roles aligned with the companion Tri-Swiss theme.
- Ask interactively for any missing rendering language or color-mode choice before generation; retain selections through refinements.
- Add four website captures and four illustrated light/dark references, with provenance and guidance that preserve subject identity.
- Make sticker backing and mode-only edits respect the selected palette.

## [1.1.0] — 2026-09-11

- Ask for a rendering language whenever a visual brief omits one.
- Return a conversation-starter help document, and nothing else, when invoked
  without a substantive visual brief.

## [1.0.0] — 2026-09-10

- Add the Lux Solari Visual Systems Director skill.
- Package the canonical visual master and 13 supporting reference boards.
- Define subject-versus-system precedence, image formats, direct generation,
  and continuity-preserving iteration.
