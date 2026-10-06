@chapter #ch-overview .dg-guide ch="1"

@page

# Design System Overview

@lede

This guide is both the living documentation of the Dimm City design system *and* a working demonstration. Every specimen on these pages is live — rendered through the same `gp-dimm-city` package as the Field Guide. This guide lives in the package's own repository and loads it in place, so reset a token in `styles/dc-palette.css`, or change a macro in `plugin.js`, and the specimen updates on the next preview refresh.

@end-lede

@section .gp-columns-2 .dc-column-panel

## How This Guide Is Organized

The guide is split into two parts.

**Part 1 — Implementation Reference** covers the token tables, CSS specifications, syntax reference, and code examples. This is what you reach for when building: look up a color token, copy a component pattern, or check what markdown syntax a container expects.

**Part 2 — Field Guide in Action** shows real Field Guide pages rendered through the same CSS. Rather than fabricated specimens, these are actual book pages — chapter openers, specialty profiles, gear spreads, stat block pages — so you can see how all the pieces come together in a real book layout.

## Design Philosophy

- **Cream pages, dark ink** — the substrate is print, not screen. All spacing, color, and type decisions are validated against paper, not a monitor.
- **Two accent registers** — Creaturepunk fire (`--crimson`, `--orange`, `--rust`) for physical content, lore, and danger; HUD digital (`--hud-blue`, `--hud-magenta`) for cybernetics, tech overlays, and system chrome.
- **Components are additive** — the base prose layer needs no class; every component class adds chrome on top of clean flowing text.

@end-section

## Design Principles

These are the north-star rules every component answers to. The full rationale lives in the [Design Constitution](https://github.com/dimm-city/gp-dimm-city/blob/main/docs/constitution.md) — read it once, start to finish, before touching the package's `styles/components/*.css`.

- **The Wall** — the page background is a brick wall in a Dimm City alley. Components are **posters and digital displays hung on it**: they sit *on top of* the page with hard edges, shadows, and decisive separation. They never bleed into the wall with soft tints or low-contrast washes.
- **Two surface registers** — every component picks ONE and stays in it. **Paper posters** (cream/paper-cream substrate, hard ink, stamps and sprays) cover banners, callouts, ledes, NPC stat blocks, and gear entries. **Digital displays** (saturated coloured fills, crisp reverse-out type, LED top-edge highlight) cover outcome chips, AP-cost chips, skill-card tabs, and alert fills.
- **Component health check** — a component is right when you could imagine peeling it off the wall as one physical object, and removing it would leave a clean rectangle of wall. It is wrong when it reads like a web `<div>` with a `background-color`, has ambiguous edges, or lets the page texture continue through it.
- **Controlled chaos (80/20)** — 80% of the page is structurally reliable (text frames, margins, tables, reading order); only 20% misbehaves (rotated stamps, broken banners, hard colour hits). Apply disruption to display elements, never to reading surfaces.

@page

## CSS Architecture

The cascade is a set of files in the `gp-dimm-city` package, loaded in the order of the package's `gutterpress.styles` list — tokens first, the book's own sheet last. Gutterpress wraps each extension's CSS in a cascade layer of its own, in `extensions:` list order — this package's is `@layer ext.gp-dimm-city` — so the `dc.*` layers below are sublayers inside that wrapper:

| File | Purpose |
|------|---------|
| `styles/dc-fonts.css` | No `dc.*` sublayer — carries the `@layer` order statement plus `@font-face` declarations |
| `styles/dc-palette.css` | `dc.tokens` layer — `:root` design tokens |
| `styles/dc-identity.css` | `dc.tokens` layer — `:root` specialty-identity tokens |
| `styles/dc-component-defaults.css` | `dc.tokens` layer — `:root` component public-token defaults |
| `styles/dc-core.css` | `dc.base` layer — `html`/`body` baseline, element resets, heading defaults |
| `styles/components/*.css` (8 files) | `dc.components` layer — every `.dc-*` component |
| `styles/page-templates.css` | `dc.templates` layer — every `.page.*` layout rule, the front-matter pages every book writes — sole home of `columns:N` |
| `styles/page-rules.css` | `dc.pages` layer — `@page` declarations, named pages, folio + chapter footers |
| `styles/dc-native.css` | No `dc.*` sublayer, last in the package — engine-specific page chrome that beats every `dc.*` sublayer |
| *the book's own sheet* — this guide's `styles/guide.css`, the Field Guide's `styles/fg-overrides.css` | Unlayered, outside the package — context overrides: chapter-id selectors that set component tokens, plus context-scoped break rules. Unlayered CSS outranks the whole `ext.gp-dimm-city` layer, so it wins **regardless of selector specificity** |

Load order: `dc-fonts.css` → `dc-palette.css` → `dc-identity.css` → `dc-component-defaults.css` → `dc-core.css` → `components/*.css` → `page-templates.css` → `page-rules.css` → `dc-native.css`, then the book's own `styles:`.

The `dc.*` sublayer order, and `dc-native.css` sitting outside it at the end of the list, only matter inside the package: that is what lets `dc-native.css` beat every `dc.*` sublayer. From the book's side the whole package is one layer, so any rule in a book's own `styles:` beats any rule in the package — `dc-native.css` included — whatever the specificity. Between a book's own sheets, specificity and then list order decide (the Field Guide lists `fg-overrides.css`, then `fg-native.css`).

To adapt for a new project, install the package (`gutterpress ext add gp-dimm-city`) and list one sheet of your own under the book's `styles:` — plain CSS, no `@layer` needed — that sets component tokens via context selectors. Never write bare `.dc-*` rules in an overrides file — that is the cascade contract.

## How Components Work

Most DC components are authored with markdown containers or plugin markers. Raw HTML is reserved for the rare structures that still do not have a markdown/plugin form. The Dimm City Gutterpress plugin adds `@skill`, `@learning-path`, `@specialty`, `@sidebar`, `@procedure`, and related block markers for structured game content.

@section .gp-columns-3 .dc-column-panel

```markdown
<!-- 1. GFM alert / markdown component -->
> [!NOTE]
> You can always spend 1 AP to delay.
```

```markdown
<!-- 2. markdown-it-container shorthand -->
@lede
This is a lede rendered via the container plugin.
@end-lede
```

```markdown
<!-- 3. Dimm City plugin markers -->
@procedure
1. Spend 2 AP.
2. Boost your next action die by one step.
@end-procedure
```

@end-section

## Customizing the Brand

`styles/dc-palette.css`, `styles/dc-identity.css`, and `styles/dc-component-defaults.css` in the `gp-dimm-city` package contain the canonical `:root` token lists. For project-specific retheming, reset the tokens you need in your book's own sheet (it is unlayered and the package sits in its own `ext.gp-dimm-city` layer, so it wins regardless of selector specificity) and set them via context selectors there.

@section .gp-columns-2 .dc-column-panel

**Before (default DC palette):**

```css
:root {
  --bg:           #c8c5bf;   /* page background — light cool gray */
  --paper-cream:  #f0eee9;   /* warm cream — primary card surface */
  --crimson:      #e1261c;   /* primary accent — vivid banner red */
  --font-display: 'lixdu', 'Tomorrow', sans-serif;
  --font-body:    'Titillium Web', Georgia, sans-serif;
}
```

**After (hypothetical alternate theme):**

```css
:root {
  --bg:           #e8e4dc;   /* warmer parchment page */
  --paper-cream:  #faf6ee;   /* lighter cream cards */
  --crimson:      #1b4f8a;   /* swap fire for HUD blue as primary */
  --font-display: 'Tomorrow', sans-serif;
  --font-body:    'Titillium Web', Georgia, sans-serif;
}
```

> [!NOTE]
> This guide re-renders every time `gutterpress preview` is running. If a component style changes in the package's `styles/components/*.css` (bump the pin, or point the manifest at a local checkout while you work), its specimen updates on the next preview refresh — no separate stylesheet to maintain.

@end-section
