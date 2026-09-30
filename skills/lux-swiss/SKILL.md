---
name: lux-swiss
description: "Style interfaces with ink, cream, and a red accent."
version: 1.1.0
author: Lux Solari (luxsolari), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design-system, swiss, minimalism, tailwind, css, typography, lux-swiss]
    related_skills: [tri-swiss]
---

# Lux Swiss — Design System

A strict, minimalist visual language: two functional colors (ink + warm cream),
one blood-red accent, Swiss-minimalist layout, visible borders, no shadows,
Space Mono / Space Grotesk typography.

Apply by default whenever building or restyling UI — React/Next/Svelte/Vue
components, HTML pages, landing pages, dashboards, buttons, cards, forms,
navigation, modals, tags, charts, or Tailwind/CSS themes.

Also trigger on: "make this look good," "style this," "apply my design system,"
"duotone," "lux swiss," "swiss," "give it a theme," or starting a new frontend
from scratch. When another design language is explicitly requested (Material,
shadcn untouched, a client's brand kit), defer to that instead.

Full component library and detailed patterns in `references/components.md`.

## Philosophy — two rules

**Duotone strict.** Ink and cream are the two functional colors; blood red is the
lone accent. No success green, no info blue, no second accent. Win/loss,
active/inactive, emphasis, error — all differentiated by weight, size, spacing,
and contrast. If you feel the urge to add a color, add a `font-bold`, a size step,
or whitespace instead.

Blood red also has a third job: a **Structural Block** — a solid-color sidebar/nav
rail or hero band (pick one per layout, capped at ~25% of viewport), plus an
independent bold-word accent inside a heading. This is not a second color — it is a
new layout job for the one accent this system already has.

The two-color segment stripe may be reused at any length as a decorative divider —
a small marker before a heading, a wider closing flourish — anywhere a purely
decorative rule would otherwise go, as long as it stays two *equal* segments,
ink then Blood Red, and is used selectively.

**Swiss-minimalist.** Borders are visible (1px solid, full ink or full cream).
No shadows — elevation comes from a background-color step (`--card` vs `--background`).
Whitespace is generous. Labels are uppercase monospace with wide letter-spacing.
Corners are mostly square.

## When to Use

Apply when this design language is requested for a UI. Use `read_file` for the
shipped theme, component patterns, and house mark; use `write_file`/`patch` to
integrate them into the approved project. If both Swiss skills are loaded and
the user has not selected a palette, ask; never apply competing defaults at once.

## Setup (three moves)

1. **Ask which font flavor.** Space (Space Mono + Space Grotesk) or Geist
   (Geist Mono + Geist Sans)? Zilla Slab is shared by both. Default to Space.
   Apply Geist by adding `.geist` to `<html>`.

2. **Install the theme.** Read `assets/theme.css` and copy its complete theme into the project's global
   stylesheet. For Tailwind 4, wire them via `@theme inline`. For non-Tailwind
   stacks, they work as plain CSS custom properties.

3. **Load the fonts.** Add the Google Fonts link for the chosen flavor — just that
   flavor's two families plus Zilla Slab, three families total unless a live toggle
   is needed.

## Palette

Always use the semantic token, never a raw hex.

### Light mode
| Token | Hex | Role |
|-------|-----|------|
| `--background` | `#f5efe0` | Page background — warm cream |
| `--foreground` | `#0a0a0a` | Body text, active controls, borders |
| `--card` | `#faf6ec` | Elevated surface |
| `--card-foreground` | `#0a0a0a` | Text on card |
| `--primary` | `#8b2e2e` | Blood red — accent, destructive, ring |
| `--primary-foreground` | `#f5efe0` | Text on primary |
| `--secondary` | `#0a0a0a` | Secondary action background |
| `--secondary-foreground` | `#f5efe0` | Text on secondary |
| `--muted` | `#ebe5d5` | Subtle backgrounds |
| `--muted-foreground` | `#4a4a48` | Subdued labels, metadata |
| `--border` | `#0a0a0a` | All borders — full ink |
| `--input` | `#faf6ec` | Input background |
| `--ring` | `#8b2e2e` | Focus ring |

### Dark mode
| Token | Hex | Role |
|-------|-----|------|
| `--background` | `#0a0a0a` | Near-black |
| `--foreground` | `#f5efe0` | Cream text |
| `--card` | `#161616` | Lifted surface |
| `--primary` | `#c04545` | Red lifted for dark contrast |
| `--secondary` | `#f5efe0` | Inverted |
| `--muted` | `#1f1f1f` | Subtle dark surface |
| `--muted-foreground` | `#a8a8a0` | Warm grey |
| `--border` | `#f5efe0` | Full cream |
| `--input` | `#161616` | — |
| `--ring` | `#c04545` | — |

Dark mode is the `.dark` class on `<html>`. Toggle with
`document.documentElement.classList.toggle("dark", isDark)` and persist under a
`theme` key in `localStorage`.

## Typography

Three roles, strictly separated, in two flavors that share the same serif.

| Role | Space (default) | Geist (flavor) | Use |
|------|------|------|-----|
| Display / mono | **Space Mono** | **Geist Mono** | Data values, tags, nav, labels |
| Body / sans | **Space Grotesk** | **Geist Sans** | Body copy, UI text, prose |
| Serif / long-form | **Zilla Slab** | **Zilla Slab** (shared) | Long-form editorial, pull-quotes |

Headings render through a fourth dependent role, `--font-display`, which defaults
to `--font-mono` until `.jost` is applied — then Jost takes over every heading
site-wide. Jost is opt-in, a single weight (700), loaded separately.

**Range comes from weight, not more typefaces.** Sans weight scale: 300 (light),
400 (regular), 500 (medium), 700 (bold — sparing, prefer 500).

**Label pattern** (pervasive): mono, `text-xs`, `uppercase`, `tracking-[0.2em]`,
weight 400 inactive / 700 active, `text-muted-foreground` → `text-foreground` active.

**Tabular figures for data:** `font-variant-numeric: tabular-nums` on numerals in
columns, tables, chart axes, stat blocks.

**Mono italic** is reserved for inline annotations and figure captions — never
emphasis (emphasis is always weight).

## Spacing & layout

- Max content width: 1000–1200px centered, `px-6` gutters.
- Radius: restrained — `0.5rem` base, rarely used. Most corners square.
- Borders: 1px solid `--border` everywhere. No shadows.
- Section header: uppercase mono label with a full-width rule beside it.

## Buttons

All buttons: `font-mono uppercase tracking-[0.2em] text-xs`. Five variants:

- **Ghost / nav** (most common): `text-muted-foreground hover:text-foreground`, no border.
- **Outlined:** `border border-foreground px-4 py-2 hover:bg-foreground hover:text-background`.
- **Filled** (primary action, rare): `border border-foreground bg-foreground px-4 py-2 text-background hover:bg-foreground/90`.
- **Destructive:** `border border-primary text-primary px-4 py-2 hover:bg-primary hover:text-primary-foreground`.
- **Accent:** `border border-primary text-primary px-4 py-2 hover:bg-primary hover:text-primary-foreground`.

**Disabled:** always `opacity-40` — never a color change.

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
- **Guardrail:** markers and borders stay neutral — ink/muted-foreground only. Never
  Blood Red as a decorative list/table marker.

## Images

- Grid placement: bordered container (1px `border-border`), consistent aspect ratio
  (4:3 or 16:9), mono-label caption beneath.
- **Default treatment:** grayscale or duotone filter — keeps the "only three color
  tokens, ever" invariant airtight.
- **Full color is permitted** specifically when the image itself is the primary content
  (a blog post's photography, a portfolio gallery, product photography) — a scoped,
  named exception, not a general license.

## Iconography

- **Lucide is the single sanctioned icon set.** No other icon library, no icon fonts,
  no emoji in UI text unless explicitly requested.
- Restyle Lucide's three defaults: `stroke-width` 2→1.5, `stroke-linecap` round→square,
  `stroke-linejoin` round→miter.
- Icons are 16–20px, `currentColor`, and **augment** the uppercase-mono labels — never
  replace them.

## Charts

- Hand-rolled SVG is the default — simple charts are ~20 lines of raw SVG.
- Colors: foreground / muted / primary only.
- When scales/axes/many-series warrant a library, the single sanctioned choice is
  **Observable Plot** (framework-agnostic SVG). Restyle to the palette; never use
  Plot's default color scheme.

## Do not

- No success green / info blue / second accent.
- No shadows.
- No chart libraries except restyled Observable Plot.
- No `rounded-full` on containers. Dots only.
- No raw hex in markup. Always the semantic token.
- No emoji in UI text unless explicitly requested.
- No accent-colored list markers or table borders.
- No full-color images outside the named photography-content exception.

## References

- `references/components.md` — full component library: status pips, modals, toggles,
  SVG chart patterns, card variants, nav patterns.

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
