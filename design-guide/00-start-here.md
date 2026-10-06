@chapter #ch-start .dg-guide

@page .dc-suppress-footer

# Dimm City Design Guide

@lede

The Dimm City design system for Gutterpress: how to write a Dimm City book in markdown, and what every macro, component, and page template looks like when it prints. Every example in this guide is live — the markdown shown is rendered by the same package the Field Guide uses, so what you see is what a book gets.

@end-lede

<div class="dc-toc">

## Part 1 — Using the system

<ol>
<li><a href="#ch-writing">Writing a Page</a> — markers, attributes, the markdown the system styles</li>
<li><a href="#ch-typography">Typography</a> — the three faces, the type scale, heading chrome</li>
<li><a href="#ch-palette">Color</a> — paper, fire and HUD tokens, and how to retheme</li>
<li><a href="#ch-layout">Layout</a> — columns, panels, sidebars, floats, break control</li>
<li><a href="#ch-text">Text &amp; Callouts</a> — ledes, flavor, pull quotes, the alert family, tape, tags</li>
<li><a href="#ch-panels">Panels, Cards &amp; Data</a> — blocks, sidebar boxes, definitions, procedures, outcomes, cards, gear, tables, stat blocks</li>
<li><a href="#ch-specialty">The Specialty System</a> — specialties, learning paths, skill cards</li>
<li><a href="#ch-templates">Page Templates</a> — chapter openers, contents, credits, catalog and profile pages</li>
<li><a href="#ch-publishing">Publishing</a> — preview, build, validate</li>
<li><a href="#ch-reference">Reference</a> — every marker on one page; options, classes, tokens</li>
</ol>

## Part 2 — A book, page by page

<ol>
<li><a href="#ch-examples">About the examples</a></li>
<li><a href="#ch-example-front-matter">Front Matter</a> — contents, credits, introduction</li>
<li><a href="#ch-example-chapter-opener">Chapter Opener</a> — fiction excerpt, citizen file walkthrough</li>
<li><a href="#ch-example-specialty-overview">Specialty Overview</a> — the specialty card grid</li>
<li><a href="#ch-example-specialty-profile">Specialty Profile</a> — intro, art, a learning path with skill cards</li>
<li><a href="#ch-example-rules">Rules &amp; Mechanics</a> — tabbed sections, definitions, conditions, the outcome ladder</li>
<li><a href="#ch-example-dm-npcs">Dream Master Pages</a> — DM notes, NPC stat blocks</li>
<li><a href="#ch-example-gear-tech">Gear &amp; Tech</a> — gear entries, callouts, an ego-point ladder</li>
</ol>
</div>

---

## How to read this guide

Every component page follows the same shape. The markdown you type is shown in a box labelled **You write**; directly beneath it, labelled **Result**, is that exact markdown rendered by the package. Options, variants, and the tokens you can retune follow in a short table. When a component only makes sense on a whole page, the page is shown in Part 2 and linked from the component.

```markdown
@lede

This is what you type.

@end-lede
```

Result {.dg-result}

@lede

This is what you type.

@end-lede

Three rules carry through the whole system, and they are worth knowing before anything else:

1. **A marker is a line that starts with `@`.** `@lede` opens a block, `@end-lede` closes it. Leave a blank line on each side of every marker.
2. **Markers take attributes** — `#id`, `.class`, and `key="value"` — in any order after the name: `@section #rules .gp-columns-2`.
3. **Classes on a parent change everything inside it.** `@specialty .augmerc` gives every card, path, and intro within it the Augmerc shape and color; nothing is set card by card.

## Quick start

Install the package into a book, write, and preview:

```sh
gutterpress new "My Book" --preset dtrpg
gutterpress ext add gp-dimm-city my-book
gutterpress preview my-book
```

Or, in the Gutterpress app: open the book, then Project settings → Features → *Install from npm* → `gp-dimm-city`. The package's macros appear in the snippet picker.

Working on the package itself? This guide loads it from the repository it lives in (`extensions: - ../` in `manifest.yaml`), so `npm run dev` at the repository root previews every change to `plugin.js` or a stylesheet here, live. The developer loop is in the repository's `docs/developing.md`.
