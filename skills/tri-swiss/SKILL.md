---
name: tri-swiss
description: "Style interfaces with governed red and turquoise accents."
version: 1.1.0
author: Lux Solari (luxsolari), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design-system, swiss, tri-tone, tailwind, css, typography, tri-swiss]
    related_skills: [lux-swiss]
---

# Tri-Swiss — Design System

A strict, minimalist visual language built around the same Space Mono / Space
Grotesk typography core as its sibling Lux Swiss (Geist Mono / Geist Sans flavor
available in both). Two structural colors (ink + cream), one strong accent
(Swiss Red), and one governed non-semantic highlight (Pastel Turquoise);
Swiss-minimalist layout, visible borders, no shadows.

Apply by default whenever building or restyling UI. Trigger on the same phrases
as Lux Swiss. When Lux Swiss or another design language is explicitly requested,
defer to that instead.

Full component library in `references/components.md`.

## Philosophy — two rules

**Tri-tone, more colorful.** Ink and cream are still the two structural colors.
Swiss Red is the primary accent — primary action, destructive, focus ring — and
now also marks section-divider rules and a selectively emphasized card/component
border (one card in a set, never the whole grid). It also has a third job: a
**Structural Block** — a solid-color sidebar/nav rail or hero band (one per layout,
capped at ~25% of viewport), plus an independent bold-word accent inside a heading.
Outside that one block, ink/cream continue to dominate.

Pastel Turquoise stays a **third, non-semantic** color — it never carries meaning
(no success/info/second-interactive-state use) — but is no longer rationed to one
touch per page: it recurs as pure decoration anywhere its presence or absence
wouldn't change what the user understands about state. It still never appears on a
button, tag, or status pip, and never as a link's own state-indicating color — though
a link may carry it as a purely decorative hover-flourish. Three guardrails keep this
from tipping into loud: ink/cream still dominate any surface; Red and Turquoise never
touch or sit adjacent on the same element; one accent per component, not both at any
single moment.

The **tri-part segment stripe** — three equal solid blocks, ink/Red/Turquoise in a
row, used for a static decorative bar (e.g. beneath a hero title) — is the one
explicitly named exception to "Red and Turquoise never touch": a single governed
device, not a general loosening. Nowhere else may the two sit adjacent. The dual-accent
hover pattern (sequential, not spatial) is the second named exception.

Turquoise also gets a genuine layout job of its own — a **Turquoise Structural Block**,
parallel to Red's but kept clearly secondary: a callout/note panel (content-sized,
may recur a few times per page), a single second-moment panel used once later in the
page flow, or a closing band used once near the page's end. These never touch or sit
adjacent to Red's own Structural Block, and their combined footprint stays visibly
smaller than Red's block wherever both appear on the same page.

The tri-part segment stripe may be reused at any length as a decorative divider — as
long as it stays three *equal* segments in ink/Red/Turquoise order and is used selectively.

**Swiss-minimalist.** Borders are visible (1px solid, full ink or full cream). No
shadows — elevation is a background-color step. Whitespace is generous. Labels are
uppercase monospace with wide letter-spacing. Corners are mostly square.

## When to Use

Apply when this design language is requested for a UI. Use `read_file` for the
shipped theme, component patterns, and house mark; use `write_file`/`patch` to
integrate them into the approved project. If both Swiss skills are loaded and
the user has not selected a palette, ask; never apply competing defaults at once.

## Setup (three moves)

1. **Ask which font flavor.** Space (Space Mono + Space Grotesk) or Geist (Geist Mono
   + Geist Sans)? Zilla Slab is shared by both. Default to Space. Apply Geist by adding
   `.geist` to `<html>`.
2. **Install the theme.** Read `assets/theme.css` and copy the complete theme into the project's global
   stylesheet. For Tailwind 4, wire via `@theme inline`. For non-Tailwind stacks, plain
   CSS custom properties.
3. **Load the fonts.** Google Fonts link for the chosen flavor — two families plus
   Zilla Slab, three families total unless a live toggle is needed.

## Palette

Always use the semantic token, never a raw hex.

### Light mode
| Token | Hex | Role |
|-------|-----|------|
| `--background` | `#f5efe0` | Page background — warm cream |
| `--foreground` | `#000000` | Body text, active controls, borders |
| `--card` | `#faf6ec` | Elevated surface |
| `--card-foreground` | `#000000` | Text on card |
| `--primary` | `#d3281b` | Swiss Red — accent, destructive, ring |
| `--primary-foreground` | `#f5efe0` | Text on primary |
| `--secondary` | `#000000` | Secondary action background |
| `--secondary-foreground` | `#f5efe0` | Text on secondary |
| `--muted` | `#ebe5d5` | Subtle backgrounds |
| `--muted-foreground` | `#4a4838` | Subdued labels, metadata |
| `--border` | `#000000` | All borders — full ink |
| `--input` | `#faf6ec` | Input background |
| `--ring` | `#d3281b` | Focus ring |
| `--highlight` | `#56bfa3` | Pastel Turquoise — governed, non-semantic |
| `--highlight-foreground` | `#000000` | Text/icon on solid `--highlight` fills |

### Dark mode
| Token | Hex | Role |
|-------|-----|------|
| `--background` | `#000000` | Near-black |
| `--foreground` | `#f5efe0` | Cream text |
| `--card` | `#161616` | Lifted surface |
| `--primary` | `#e2503f` | Red lifted for dark contrast |
| `--secondary` | `#f5efe0` | Inverted |
| `--muted` | `#1f1f1f` | Subtle dark surface |
| `--muted-foreground` | `#a8a696` | Warm grey |
| `--border` | `#f5efe0` | Full cream |
| `--input` | `#161616` | — |
| `--ring` | `#e2503f` | — |
| `--highlight` | `#63cbae` | Pastel Turquoise, lifted for dark mode |
| `--highlight-foreground` | `#000000` | Same constant black |

Dark mode is the `.dark` class on `<html>`. Toggle with
`document.documentElement.classList.toggle("dark", isDark)` and persist under a
`theme` key in `localStorage`.

### The `--highlight` token — read this before using it

Pastel Turquoise carries **zero semantic meaning** — never success, never info, never
a second interactive state. Unlike Swiss Red, it is never the answer when an element
needs to signal something. It IS sanctioned for open-ended **decorative** reuse:

1. A second data series/stroke in a hand-rolled SVG or Observable Plot chart.
2. A brand/hero moment (e.g. a hero accent or a logo mark).
3. An icon fill on a single icon, used as a flourish rather than a state cue.
4. An underline or rule beneath a heading or label.
5. A background wash (e.g. `bg-highlight/10`) behind a block that wants separation
   without a hard border.
6. A dot accent, matching the existing dot-indicator pattern.
7. A hover-triggered flourish on a nav link or label — an underline or dot that appears
   on `:hover`, purely ornamental and identical regardless of active/current/visited
   state, layered *alongside* the element's existing ink/muted-foreground hover color
   change (which still carries the real interactive feedback).
8. A card's border plus a subtle background wash (the Accent card) — still purely
   decorative, not a semantic "this card matters more" cue.

It can recur multiple times on the same page — the old "exactly one brand moment" cap
is gone — but the test that governs every use is unchanged: if turquoise's presence or
absence would change what the user understands about *state*, it's wrong. If it's purely
ornamental and removable without changing meaning, it's fine.

**Do not** use it as a button's, tag's, status pip's, or link's own state-indicating
color. A link may show a decorative Turquoise hover-flourish *in addition to* its real
ink/red state feedback — Turquoise itself never signals the state.

## Typography

Three roles, strictly separated, in two flavors that share the same serif.

| Role | Space (default) | Geist (flavor) | Use |
|------|------|------|-----|
| Display / mono | **Space Mono** | **Geist Mono** | Data values, tags, nav, labels |
| Body / sans | **Space Grotesk** | **Geist Sans** | Body copy, UI text, prose, dense-data text |
| Serif / long-form | **Zilla Slab** | **Zilla Slab** (shared) | Long-form editorial, pull-quotes |

Headings render through a fourth dependent role, `--font-display`, which defaults to
`--font-mono` until `.jost` is applied — then Jost takes over every heading site-wide.
Jost is Tri-Swiss's own original register, opt-in, a single weight (700), loaded
separately. Unlike `.geist`, `.jost` is not a flavor: it composes independently with
either flavor and with `.dark`.

**Range comes from weight, not more typefaces.** Sans weight scale: 300 (light),
400 (regular), 500 (medium), 700 (bold — sparing, prefer 500).

**Label pattern** (pervasive): mono, `text-xs`, `uppercase`, `tracking-[0.2em]`,
weight 400 inactive / 700 active, `text-muted-foreground` → `text-foreground` active.

**Tabular figures for data:** `font-variant-numeric: tabular-nums` on numerals in
columns, tables, chart axes, stat blocks.

**Mono italic** is reserved for inline annotations and figure captions — never emphasis.

## Spacing & layout

- Max content width: 1000–1200px centered, `px-6` gutters.
- Radius: restrained — `0.5rem` base, rarely used. Most corners square.
- Borders: 1px solid `--border` everywhere. No shadows.
- Section header: uppercase mono label with a full-width rule beside it. The rule is
  `bg-border` by default; swap to `bg-primary` for a section that earns emphasis
  (used selectively — one or two per page, never on every divider).

## Buttons

All buttons: `font-mono uppercase tracking-[0.2em] text-xs`. Five variants:

- **Ghost / nav** (most common): `text-muted-foreground hover:text-foreground`, no border.
- **Outlined:** `border border-foreground px-4 py-2 hover:bg-foreground hover:text-background`.
- **Filled** (primary action, rare): `border border-foreground bg-foreground px-4 py-2 text-background hover:bg-foreground/90`.
- **Destructive:** `border border-primary text-primary px-4 py-2 hover:bg-primary hover:text-primary-foreground`.
  Demonstrates the hover hierarchy: Red carries the real hover signal.
- **Accent:** `border border-primary text-primary px-4 py-2 hover:bg-highlight hover:text-highlight-foreground hover:border-highlight`.
  Red border at rest, Turquoise on hover: the dual-accent hover exception, not a decorative
  flourish.

**Disabled:** always `opacity-40` — never a color change.

## Hover states

Wherever a hover state uses an *accent* color — not just an ink/muted-foreground tone
shift — to signal interactivity, **Red is the only color permitted to carry that real
signal.** Turquoise never signals on its own in a hover state; it may only layer in as a
purely decorative flourish alongside Red's or ink's real feedback. This doesn't require
every hoverable element to use an accent color: most buttons/tags/toggles hover via
ink/muted-foreground shifts only.

**The one named exception: dual-accent hover.** The Accent button above and the Interactive
card (see `references/components.md`) swap Red for Turquoise on hover — Red border at rest,
Turquoise border/fill on hover. This is a genuine, deliberate exception scoped to exactly
these two patterns. The two colors are never visible on the element simultaneously (a state
transition, not spatial adjacency), so it doesn't touch the separate "Red and Turquoise
never touch" guardrail — but it is a real carve-out, not a decorative layer, and must not
spread beyond these two named patterns.

## Tags / pills

Small inline badges: `font-mono text-[0.65rem] px-2 py-0.5 uppercase tracking-[0.12em]`.

- **Neutral:** plain text, `text-muted-foreground`.
- **Signal:** `bg-foreground text-background`.
- **Outlined:** `border border-dashed border-foreground/50 text-foreground/80`, 4px dot prefix.
- **Saved:** `border border-foreground/30 text-foreground/50`, 4px dot prefix.

`rounded-full` is reserved for dot indicators only — never on containers or pills.

## Lists / tables

- **Lists:** no round bullets. Unordered items get a thin top-border divider between rows.
  Ordered items use tabular mono numbers + body-font text.
- **Tables:** bold mono header row, 2px bottom border, 1px `border-border` between rows,
  `tabular-nums` right-aligned for numeric columns. No zebra striping.
- **Guardrail:** markers and borders stay neutral — ink/muted-foreground only. Never Red or
  Turquoise as a decorative list/table marker.

## Images

- Grid placement: bordered container (1px `border-border`), consistent aspect ratio
  (4:3 or 16:9), mono-label caption beneath.
- **Default treatment:** grayscale or duotone filter — keeps the "only four color tokens,
  ever" invariant airtight.
- **Full color is permitted** specifically when the image itself is the primary content
  (a blog post's photography, a portfolio gallery, product photography) — a scoped, named
  exception, not a general license.

## Iconography

- **geist-icons is the single sanctioned icon set.** No other icon library, no icon fonts,
  no emoji in UI text unless explicitly requested.
- Restyle geist-icons' three defaults: `stroke-width` 2→1.5, `stroke-linecap` round→square,
  `stroke-linejoin` round→miter.
- Icons are 16–20px, `currentColor` (`primary` only for the destructive/accent cases already
  reserved for it — never `highlight`), and **augment** the uppercase-mono labels — never
  replace them.

## Charts

- Hand-rolled SVG is the default — simple charts are ~20 lines of raw SVG.
- Colors: foreground / muted / primary only, **except** when a chart genuinely has a second
  data series worth distinguishing — that series, and only that one, may use `--highlight`.
- When scales/axes/many-series warrant a library, the single sanctioned choice is **Observable
  Plot** (framework-agnostic SVG). Restyle to the palette: `--highlight` only for a genuine
  second series. Never use Plot's default color scheme.

## Do not

- No third semantic color. `--highlight` is not success green or info blue in disguise.
- No accent-colored hover signal other than Red. Turquoise may only decorate a hover state,
  never carry its meaning alone.
- No shadows.
- No chart libraries except restyled Observable Plot.
- No `rounded-full` on containers. Dots only.
- No raw hex in markup. Always the semantic token.
- No emoji in UI text unless explicitly requested.
- No Turquoise on buttons, tags, status pips, or links as their default/rest color.
- No red-and-turquoise simultaneously on the same element. Pick one accent per component at
  any single moment — the tri-part stripe (spatial) and the dual-accent hover pattern
  (sequential) are the two named exceptions, not a general loosening.
- No accent-colored list markers or table borders.
- No full-color images outside the named photography-content exception.
- Ink/cream still dominate. Accents are seasoning; a surface where Red or Turquoise
  out-covers ink/cream has gone too far.

## References

- `references/components.md` — full component library: status pips, modals, toggles, SVG
  chart patterns, card variants (Accent card, Interactive card), nav patterns.

## Pitfalls

- Paths are relative to this SKILL.md: `assets/theme.css`,
  `references/components.md`, and `references/HOUSE-MARK.md` are shipped.
  Do not look under an upstream `skills/<name>/` nesting inside this skill.
- The stylesheet includes Tailwind 4 directives. For plain CSS retain the token
  blocks (`:root`, `.dark`, `.geist`, `.jost`), remove Tailwind-only `@import`,
  `@custom-variant`, `@theme inline`, and any `@apply` blocks, then map font roles
  and body/heading styling explicitly. Tailwind tokens alone do not load fonts
  or style headings; apply `font-display` or `font-family: var(--display)`.
- Load real font resources for the chosen flavor, shared Zilla Slab, and optional
  Jost 700. CSS font names are not downloads. Offline/self-hosted fonts need
  explicit assets/licenses; fallbacks are not proof of visual fidelity.
- Full upstream typography/heading/house-mark instructions are preserved in
  `references/source-SKILL.md`; load the relevant sections when applying them.
  Design/house-mark usage also carries `LICENSE-DESIGN`, separate from code MIT.
- A skill supplies design instructions, not automatic theme injection, fonts,
  a registered slash command, or a visual-rendering runtime.

## Verification

Run `python3 -m unittest discover -s "<skill-root>/tests" -v` via `terminal` for
static theme contracts. In a real project compile CSS and inspect light/dark,
font-flavor, optional Jost headings, accent limits, borders, and keyboard focus.
Static tests do not prove contrast/accessibility or rendered fidelity.
