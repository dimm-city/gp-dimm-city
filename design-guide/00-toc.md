@chapter #ch-toc .dg-guide

# Dimm City Design Guide

@lede

This is the Dimm City print design system — cyberpunk and creaturepunk, built on Gutterpress. Everything in these pages is live: the type, color, and components you see here are rendered through the same CSS as the Field Guide. The guide has two parts: **Part 1** is the implementation reference — token tables, CSS specs, and syntax you reach for while building. **Part 2** is real Field Guide pages rendered through that same CSS — see how all the pieces come together in an actual book.

@end-lede

<div class="dc-toc">

## Part 1 — Implementation Reference

<ol>
<li><a href="#ch-overview">Design System Overview</a> — how to use this guide</li>
<li><a href="#ch-typography">Typography</a> — display, mono, body; type scale</li>
<li><a href="#ch-palette">Color Palette</a> — paper, fire, HUD, surface tokens</li>
<li><a href="#ch-components">Components</a> — callouts, pull quotes, tables, plus the DC and Field Guide component libraries (skill cards, stat blocks, definition blocks, gear entries)</li>
<li><a href="#ch-templates">Page Templates</a> — named page types, chapter openers</li>
<li><a href="#ch-layout">Layout &amp; Composition</a> — columns, floats, break utilities</li>
<li><a href="#ch-reference">Markdown Reference</a> — all syntax with examples</li>
<li><a href="#ch-cli">Publishing</a> — print export, DTRPG preset, PDF validation</li>
<li><a href="#ch-gallery">Component Gallery</a> — live render of every component, full variants</li>
</ol>

## Part 2 — Field Guide in Action

<ol>
<li><a href="#ch-examples">Examples Overview</a> — how to read these pages</li>
<li><a href="#ch-example-front-matter">Front Matter</a> — credits, TOC, intro</li>
<li><a href="#ch-example-chapter-opener">Chapter Opener</a> — chapter start spreads</li>
<li><a href="#ch-example-specialty-overview">Specialty Overview</a> — chapter intro pages</li>
<li><a href="#ch-example-specialty-profile">Specialty Profile</a> — full specialty spread</li>
<li><a href="#ch-example-rules">Rules &amp; Mechanics</a> — dice, outcomes, distances</li>
<li><a href="#ch-example-dm-npcs">Dream Master Pages</a> — NPC stat blocks, encounter hooks</li>
<li><a href="#ch-example-gear-tech">Gear &amp; Tech</a> — weapons, tables, cybernetics</li>
</ol>
</div>

---

## Quick Start

1. The brand tokens live in the `gp-dimm-city` package: `styles/dc-palette.css` (plus `styles/dc-identity.css` for specialty-identity tokens and `styles/dc-component-defaults.css` for component public-token defaults) — colors, fonts, and spacing are the `:root` blocks at the top of those files. A book retunes them in its own sheet, listed under `styles:` and left unlayered; it never edits the package.
2. Open `design-guide/` in the Gutterpress app, or run `npm run dev` from the repository root, to see your changes live. The guide loads the package from this repository (`extensions: - ../` in its manifest), so an edit to a stylesheet or to `plugin.js` is on screen at the next refresh — no release, no pin.
3. Remove or add chapters to `manifest.yaml` as needed — the guide only documents what you actually ship.

## Quick Start — What Each Chapter Covers

### Part 1 — Implementation Reference

| Chapter | Covers |
|---------|--------|
| **1 — Design System Overview** | Guide structure, CSS architecture, component model, how to customize the brand |
| **2 — Typography** | Typefaces, type scale, heading styles, body prose, code blocks, and font tokens |
| **3 — Color Palette** | All `--crimson`, `--hud-blue`, surface, and text tokens; contrast ratios; usage rules |
| **4 — Components** | Alerts, callouts, sidebars, procedures, definitions, tables, plus the DC Component Library (specialty cards, skill cards, learning paths, chapter openers) and Field Guide Components (definition blocks, gear entries, stat grids) — sections within this one chapter |
| **5 — Page Templates** | Every named page layout: `page-chapter-start`, `citizen-file`, `spread-gear`, and more |
| **6 — Layout & Composition** | Column breaks, two-column and three-column grids, `.gp-no-break`, flow utilities |
| **7 — Markdown Reference** | Full macro syntax — every `@macro` / `@end-macro` pair with usage examples |
| **8 — Publishing** | Print export, DTRPG preset, PDF validation, asset requirements |
| **9 — Component Gallery** | Live render of every component with full variants (mirrors the production source) |

### Part 2 — Field Guide in Action

| Chapter | Covers |
|---------|--------|
| **Examples Overview** | How real-world examples are organized and what pages to reference |
| **Front Matter** | Title spread, legal page, ToC layout |
| **Chapter Opener** | Chapter-start two-column spread and Citizen File info page |
| **Specialty Overview** | Specialty intro spread and overview layout |
| **Specialty Profile** | Full specialty profile with skill cards and learning path |
| **Rules & Mechanics** | Action economy, combat, and multi-column rules content |
| **Dream Master Pages** | DM notes, NPC stat blocks, and encounter tables |
| **Gear & Tech** | Gear card grids and equipment reference spreads |
