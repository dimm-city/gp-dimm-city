# CSS roadmap

What remains from the CSS architecture review of October 2026, and what is already done. Each item lists its review number. `docs/cleanup-backlog.md` holds styling that is unused but kept pending a decision.

Every change follows the same verification:
- `bun test` passes with 0 fail;
- the design guide and the Field Guide are rebuilt with the gutterpress CLI;
- page counts are unchanged;
- every page is compared with a baseline build, and any visible change is intended and named.

## Done

| Release | Items |
|---|---|
| 1.1.1 | Opaque colours for PDF/X-1a. Specialty chapters nest in the outline. |
| 1.1.2 | The quick wins (review items 1–10): dead shadows and declarations, `--shadow-ink` and the `--tint-*` tokens, one masthead rule. Section chrome as tokens, with templates owning their own chrome (12, 13). One `break-inside` token (11). `.dc-snug`, the split-card rules and `.dc-cards-two-col` promoted from the Field Guide (18). Integrity tests (23). gutterpress 0.11.15. |
| 1.1.3 | Distance tags and six unused style combinations removed. |
| 1.1.4 | The columns contract was refined: components may set columns on their own internals. The integrity test's exception lists shrank to genuine hooks. |

## Next: medium (days each)

The chapter prefix and the offset tokens are parked under "Still considering" in `cleanup-backlog.md`.

- **Chapter prefix (15).** Make the chapter prefix and the footer-chip chrome configurable, so the design guide can drop the six `@page` blocks and four chip resets it restates.
- **Offset tokens (14).** Add `--dc-outline`, `--dc-chrome-bleed` and `--dc-z-*`, then derive the hard-coded offsets from them. The "-2px to cancel the 2px outline" offsets are an example.
- **Wall utility (16).** Add a `.dc-wall` utility and use it in the design guide's stages.
- **One file per component (17).** Each component lives in one file, and each file is named for what it holds. The rules for the chevron and masthead, TOC, colophon, AP chip, sidebar and path shell are currently spread across several sheets.
- **Gradients in PDF/X (19).** Raster artwork on a split page is accepted (constitution §V), so a gradient being rasterised is no longer the concern. What stays off limits is a `repeating-*` or `conic-gradient()` (the page falls back to whole-page flattening and loses its live text) and a gradient with transparent stops (Chromium writes a type-1 shading PDF.js cannot read; the gloss was pre-mixed for that in 1.10.2). The tape dashes are already an ordinary gradient tiled by `background-size`. Replace a gradient only where a flat form looks the same and is simpler.

## Later: larger (a sprint each, with visible risk)

- **Scope the element baseline (20).** Bare `p`, `table`, `hr`, `blockquote` and the headings stop carrying decoration, so components stop undoing it. This is the root cause of most of the remaining overrides.
- **Specialty shapes (21).** Replace about 70 hand-written polygons with a parameterised shape system.
- **`dc-` prefix (22).**
  - The template classes are done: 1.5.0 declares them as page words (`@page intro` writes `dc-page-intro`, and so on) and no longer styles the old `.page-intro`, `.page-toc`, `.page-credits` spellings. What is left is the bare modifiers (`.warning`, `.free`, `.variable`).
  - Ship aliases for one release.
  - This touches all three books, and the owner wants it as its own change.

## Book-side work

- **Field Guide: specialty-card pages.** These pages are scheduled for a redesign.
- **Field Guide: sidebars.** Choose sidebar areas. `@sidebar-box` suits short asides that stay in the text flow. The inset rail was removed 2026-10-12.
- **Field Guide: art.**
  - Eight pages have art below 300 DPI.
  - Cutout art with an alpha channel is rasterised with the page's other artwork under `preserve-text`, text kept live; only a page that shows no text is flattened whole, and nothing is lost there.

## Known, accepted warnings

`gutterpress validate design-guide --phase pre-build` passes with no warning and three notes (1.10.2-alpha.2, Gutterpress 0.11.24-alpha.1):

- **Three "Ellipsis character (U+2026)" notes** (`08-page-templates.md:41`, `10-reference.md:17` and `:63`). Each is the range `wall-1 … wall-13` in a reference table, typed with the character on purpose. They are informational and are left as they are.

What this section used to list, and where it went:

- **The "heading level jump" warnings** (the first heading inside a rendered component example, where a skill card, stat block, walkthrough or sidebar box requires an `h4`; the Part 2 example chapters, which jump `h2` to `h4` as specimens of book pages). Since 1.10.2-alpha.2 the guide turns them off by configuration: `checks: source.accessibility.heading-order: off` in its manifest, and `MD001` and `MD024` off in the repository's `.markdownlint.jsonc`. The per-project setting the earlier note said was missing ([dimm-city/gutterpress#339](https://github.com/dimm-city/gutterpress/issues/339)) is the manifest's `checks:` map.
- **The `printsafe/no-risky-print-effects` warnings on `clip-path` (about 33) and the `page-containment` warning on the scoped `.page` clip.** Neither appears any more: Gutterpress's rule no longer lists `clip-path` as a property that forces rasterisation (it flags `filter`, the blend modes, animation and `will-change`), and the containment warning is gone with it. Nothing in the package changed for either.

## Keep (what works)

- **Layering.** Named sublayers are declared once, gutterpress wraps the package in `ext.<name>`, and book sheets sit unlayered on top. There is no `!important` anywhere.
- **The token contract (dc#34).** Public tokens have their defaults at `:root`. Components read them with a bare `var()`. Variants and contexts set tokens rather than overriding properties.
- **Print discipline.**
  - Clipped sibling layers.
  - Nothing a box paints extends above that box.
  - Opaque text colours and no repeating or transparent-stop gradients, enforced by tests (*keep text opaque*, *use no repeating gradient*). Translucent artwork is allowed and prints as a 300 DPI picture on its page (constitution §V).
  - Accent rails drawn as inset shadows rather than gradients.
- **Fragmentation care.** The heading look classes, the `.gp-columns-flow` fix, and the zero-specificity `flow-root`.
- **Measured comments and an honest catalog.** Comments record real measurements, and `components.yaml` carries honest statuses.
