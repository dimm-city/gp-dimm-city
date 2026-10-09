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

- **Chapter prefix (15).** Make the chapter prefix and the footer-chip chrome configurable, so the design guide can drop the six `@page` blocks and four chip resets it restates.
- **Offset tokens (14).** Add `--dc-outline`, `--dc-chrome-bleed` and `--dc-z-*`, then derive the hard-coded offsets from them. The "-2px to cancel the 2px outline" offsets are an example.
- **Wall utility (16).** Add a `.dc-wall` utility and use it in the design guide's stages.
- **One file per component (17).** Each component lives in one file, and each file is named for what it holds. The rules for the chevron and masthead, TOC, colophon, AP chip, sidebar and path shell are currently spread across several sheets.
- **Gradients in PDF/X (19).** The outcome keys and tabbed headings print as 360×180 ppi images in PDF/X, and the tape dashes use a hard-stop gradient. Replace them where a flat or vector form looks the same.
- **Chapter-opener padding.** A second section on a chapter-opener page inherits the opener's padding, but its header bar cancels its own. This is how it always worked; it was kept for pixel identity in 1.1.2.

## Later: larger (a sprint each, with visible risk)

- **Scope the element baseline (20).** Bare `p`, `table`, `hr`, `blockquote` and the headings stop carrying decoration, so components stop undoing it. This is the root cause of most of the remaining overrides.
- **Specialty shapes (21).** Replace about 70 hand-written polygons with a parameterised shape system.
- **`dc-` prefix (22).**
  - Covers the template classes (`.page-intro`, `.page-toc`, `.page-credits`, `.credits-colophon`) and the bare modifiers (`.warning`, `.inset`, `.free`, `.variable`).
  - Ship aliases for one release.
  - This touches all three books, and the owner wants it as its own change.

## Book-side work

- **Field Guide: specialty-card pages.** These pages are scheduled for a redesign.
- **Field Guide: sidebars.** Choose sidebar areas. `@sidebar-box` suits short asides that stay in the text flow. An inset sidebar suits a long aside that runs alongside the text on its own page. The inset rail rules wait on this decision (see `cleanup-backlog.md`).
- **Field Guide: art.**
  - Eight pages have art below 300 DPI.
  - Cutout art with an alpha channel still flattens a few pages in PDF/X-1a.

## Keep (what works)

- **Layering.** Named sublayers are declared once, gutterpress wraps the package in `ext.<name>`, and book sheets sit unlayered on top. There is no `!important` anywhere.
- **The token contract (dc#34).** Public tokens have their defaults at `:root`. Components read them with a bare `var()`. Variants and contexts set tokens rather than overriding properties.
- **Print discipline.**
  - Clipped sibling layers.
  - Nothing a box paints extends above that box.
  - Opaque `color-mix` composites, enforced by a test.
  - Accent rails drawn as inset shadows rather than gradients.
- **Fragmentation care.** The heading look classes, the `.gp-columns-flow` fix, and the zero-specificity `flow-root`.
- **Measured comments and an honest catalog.** Comments record real measurements, and `components.yaml` carries honest statuses.
