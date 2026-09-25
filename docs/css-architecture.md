# dc-design-guide — CSS Architecture & Patterns

This document defines the CSS authoring conventions for the dc-design-guide and any
project that adapts it. It is the normative reference for all structural decisions —
when in doubt, consult this document before touching the source files.

---

## 1. Print-First Philosophy

This is a print document system. There are no `@media screen` rules, no responsive
breakpoints, no hover states. The output medium is a PDF paginated by Chromium's own
native print engine, and every rule must survive that pipeline unchanged.

**Physical units everywhere.** All sizing uses `pt` or `in` — units that map directly
to physical paper. `px` appears only for border widths where sub-point precision is
useful (`--bw-thin: 1px`, `--callout-border-width-small: 2px`). Component chrome dimensions (tab labels, icon badges, stat-cell keys) also use `px` where visual relationship to the surrounding layout matters more than physical print size — `9px` for a label superscript reads consistently at all print zoom levels. Avoid `em` for layout
geometry (column widths, gutters, card padding) — use `0.25in` not `1.5em`. The
exception is typographic rhythm: heading margins and padding that should scale
proportionally with the heading's own font-size (`h1, h2, h3 { margin: 1.5em 0 0.5em }`)
are correctly expressed in `em`. Bullet gaps and inline padding on `code` elements are
also correct uses of `em`. The rule is about column geometry, not typographic spacing.

**The design guide is the canonical test bed.** If you are unsure how a rule renders,
add a specimen to the design guide's own sheet (`@layer book`) and build a preview.

---

## 2. The CSS Layer Stack

The stylesheet cascade is a set of files, each wrapped in one CSS **cascade
layer** (`@layer`, adopted dc#54), loaded in the explicit order of
`package.json`'s `gutterpress.styles` array. No file imports another; the
manifest array is the only place the order is written down.

**Package boundary.** This whole repository is the Gutterpress extension
package `gp-dimm-city`. A book installs it with `gutterpress ext add
gp-dimm-city` (or from the app's Features panel), which pins the exact
version and vendors a copy under the book's `plugins/npm/`. The cascade a
consuming book gets is core (layered) → the sixteen package sheets in
`gutterpress.styles` order → the book's own `styles:` last (gutterpress#265).
Anything a single book needs — a design guide's demo scaffolding, a field
guide's chapter-specific art — lives in that book's own sheet, wrapped in
`@layer book`, never in this package.

The layer names and order are declared **once**, as a statement in
`dc-fonts.css` — the first sheet the cascade sees — so layer order never
depends on file order:

```css
/* styles/dc-fonts.css — before any rule */
@layer dc.tokens, dc.base, dc.components, dc.templates, dc.pages, book;
```

Each file below is wrapped in the one layer it names. Layer order settles
cross-file ties — a rule in a later layer wins **regardless of selector
specificity**, which is what makes the stack order-proof: moving a file
earlier or later in the array, or splitting one file into several, cannot
silently flip which sheet wins a shared selector.

```jsonc
// package.json → gutterpress.styles
"styles/dc-fonts.css",                        // UNLAYERED — see below
"styles/dc-palette.css",                      // @layer dc.tokens
"styles/dc-identity.css",                     // @layer dc.tokens
"styles/dc-component-defaults.css",           // @layer dc.tokens
"styles/dc-core.css",                         // @layer dc.base
"styles/components/callouts.css",             // @layer dc.components
"styles/components/specialty-identity.css",   // @layer dc.components
"styles/components/chrome.css",               // @layer dc.components
"styles/components/cards.css",                // @layer dc.components
"styles/components/specialty.css",            // @layer dc.components
"styles/components/data.css",                 // @layer dc.components
"styles/components/images.css",               // @layer dc.components
"styles/components/section.css",              // @layer dc.components
"styles/page-templates.css",                  // @layer dc.templates
"styles/page-rules.css",                      // @layer dc.pages
"styles/dc-native.css"                        // UNLAYERED, last — see below
```

`book` is declared last and holds no package file: it is the layer for a
consuming book's own sheets. Because it is the last-declared layer, a rule in
`book` wins every cross-layer tie without a specificity contest. A book must
not invent further layer names — a layer this statement does not name is
created where it is first used, which places it *after* `book`, silently
above the book's own overrides.

**Two sheets are deliberately UNLAYERED.** `dc-native.css` is the last
entry in the array and carries the engine-specific native-print chrome
(margin-box chip styling, the brick margin band, native-print break fixes).
Unlayered CSS always outranks layered CSS, no matter which layer, no matter
specificity — that is the ONE piece of the cascade stronger than any
`@layer` — so it beats every layered sheet in the package *and* the book's
`@layer book` overrides. The same rule cuts the other way: **any unlayered
rule in a book's own `styles:` list also beats every layered sheet**, which
is exactly how a book overrides `dc-native.css` when it must — an unlayered
sheet listed after the extension (the field guide's `fg-native.css` is one).
`dc-fonts.css` is the other unlayered file, for an unrelated reason: it
carries the `@layer` statement (which must be a top-level statement, not
nested inside a layer) and its only rules are `@font-face`, where a layer
would be pointless — font-family lookup is not a cascade contest.

### Layer Responsibilities

| Layer | Files | Owns | Must NOT contain |
|---|---|---|---|
| `dc.tokens` | `dc-palette.css`, `dc-identity.css`, `dc-component-defaults.css` | `:root` token blocks (palette primitives, specialty-identity aliases, component public-token defaults) | `@page` rules, `.dc-*` components, `.page.*` layout rules, html/body baseline |
| `dc.base` | `dc-core.css` | html/body baseline, global element resets, heading defaults, `* { print-color-adjust }` | `@page` rules, `.dc-*` components, `.page.*` layout rules |
| `dc.components` | `components/{callouts,specialty-identity,chrome,cards,specialty,data,images,section}.css` | Every `.dc-*` component class (base + token contracts + thin variants), specialty parent-container overrides | `columns:N` rules, `@page` declarations, `div.chapter` scaffolding |
| `dc.templates` | `page-templates.css` | ALL **theme** `columns:N` rules (exclusive ownership), `.page.*` content layout including the front-matter pages every Dimm City book writes (contents, credits, chapter start), page wrapper scaffolding, print utilities, `.dc-specialty` break control | `@page` declarations, `.dc-*` component styles, `:root` tokens, `columns` on core's `.gp-columns-*` (gap only, via `--gp-column-gap`) |
| `dc.pages` | `page-rules.css` | Every `@page` declaration, named-page geometry, margin-box content (folio + chapter footers), the `string-set` producer for the chapter footer label | Component styles, token definitions, `columns:N` rules |
| `book` | *the consuming book's own sheets* (none in this package) | Book context overrides — chapter-id token selectors, context-scoped break rules, a design guide's demo scaffolding; last-declared layer, so it wins every cross-layer tie | Bare `.dc-*` component rules, `:root` token definitions, `columns:N` rules |
| *(unlayered)* | `dc-fonts.css`, `dc-native.css`, and any unlayered sheet a book lists after the extension | `@font-face` and the `@layer` statement (`dc-fonts.css`); engine-specific native-print chrome that must beat every layered sheet AND any layered book CSS (`dc-native.css`) | Anything that should lose to a later book override — unlayered CSS cannot be outranked by any layer |

### COLUMNS:N Ownership Rule

Among the theme's own sheets, `columns:N` lives **exclusively** in
`page-templates.css` (`@layer dc.templates`). Every other file is
single-flow. If you find `columns:` in a `components/*.css` file,
or `page-rules.css`, it is a bug.

**The generic column vocabulary is not the theme's at all.** Gutterpress core
ships `.gp-columns-2` / `.gp-columns-3` in `GUTTERPRESS_CSS`, and a theme may
not define competing generic names or re-declare `columns` on core's
(gutterpress `CLAUDE.md` §6). This theme used to ship `.two-column` /
`.three-column`, which did exactly that; they were removed 2026-08-21.
`page-templates.css` now sets only the **gap**, through core's author hook
(`--gp-column-gap`), and `dc-native.css` owns the per-shape
`column-fill` decisions.

The name was carrying two jobs, which is why the fix was not a rename:

| Concern | Owner | Class |
|---|---|---|
| How many columns, and the gap | Gutterpress core (theme sets `--gp-column-gap`) | `.gp-columns-2` / `.gp-columns-3` |
| The card around a column run — substrate, top/bottom rules, spanning heading bar, shared preamble paragraph, gear-entry min-heights | `components/section.css` (`@layer dc.components`) | `.dc-column-panel` |

Authors write both when they want the card: `@section .gp-columns-2 .dc-column-panel`.
A column run with no chrome is `@section .gp-columns-2` on its own — which is
the point of separating them.

### Layer Contract Rules

**Tokens flow downward only.** The `:root` block is the exclusive property of
the `dc.tokens` layer (`dc-palette.css`, `dc-identity.css`,
`dc-component-defaults.css`). No other layer defines custom properties on
`:root`. All layers consume tokens via `var(--token)`. a book's `@layer book` sheet's
`book` layer — the last-declared layer — is the only sanctioned override
path — do not edit the `dc.tokens` files for project-specific changes.

**No upward `!important` fights.** Layers do not override each other with
`!important`, and a layer-order flip is never fixed with `!important` either
— see "Cascade layers, not just file order" below. Margin-box content is
plain `@page` cascade: one block per named page wins on the page selector
alone (see `page-rules.css`'s "ONE BLOCK PER NAMED PAGE" contract).

**Selector ownership is exclusive.** If you are writing a rule for `.dc-callout`, it
belongs in `components/callouts.css` (`@layer dc.components`). If you are writing
an `@page` rule — including the page background — it belongs in `page-rules.css`
(`@layer dc.pages`). If you are writing a selector that only exists for a rendered
design-guide example, it belongs in the design guide's own sheet (`@layer book`).
A `.dc-*` selector in `page-rules.css` is a bug.

**Cascade layers, not just file order (dc#54).** Layer order decides a
cross-layer tie **regardless of selector specificity** — a one-class rule in
`book` beats a three-class rule in `dc.components`. This is what makes the
stack immune to reordering the `gutterpress.styles` array or splitting a file in two, but it
also means a rule written assuming "my file loads later, so my higher
specificity wins" can flip the moment two sheets end up in different
layers. When two rules genuinely need to compete for the same property on
the same element, that is a bug regardless of layers — fix it by giving the
correct rule ownership of the property outright (per "Selector ownership is
exclusive" above), or by increasing/decreasing specificity **within the
rule that should win's own layer**. Never reach for `!important`, and never
pull a sheet out of its layer to "fix" a flip — that reopens the exact
specificity-order fragility layers exist to close. If a genuine one-off
diff survives a real fix attempt, waive it in
the consuming book repo's render-parity waivers with a reason that names the two
competing rules and why the new (layered) winner is correct — do not carry
an unexplained visual regression forward just to keep a diff count at zero.

**Reusable components use a real base class plus thin variants.** For shared UI
systems like alerts, banners, panels, and stat grids, the canonical dc-prefixed
base class owns the full default shell. Variant classes should only override the
few properties that actually change.

Use CSS custom properties only when they form a small documented public API for a
component, such as surface, accent, foreground, label text, or title color.
Do not expose internal layout details like padding, margin, width, line-height,
break behavior, or label typography as broad variable APIs by default.

Important: visually related components are not automatically one component
family. In the dc-design-guide, `.dc-skill-card`, `.dc-path-shell`, and
`.dc-specialty-card` are distinct components and should not be forced into one
large variable-driven abstraction.

---

## 3. The Token System

All design decisions that recur in two or more rules are expressed as custom
properties in the `:root` block of `dc-palette.css`. The taxonomy follows a strict
hierarchy: color → typography → spacing → geometry.

### Color Tokens

```css
/* Semantic brand colors — names carry meaning, not just hex values */
--crimson:        #e1261c;  /* PMS Red 032 — CMYK 0 95 90 0; survives POD */
--blood:          #901a12;  /* oxidised arterial — heading color */
--orange:         #d4500a;  /* burnt circuit-board — heat-damaged, not friendly cone */
--rust:           #b23a12;  /* burnt rebar edge */
--amber:          #7a5a20;  /* sulfur-scorched brass — contaminated, not generic earth */
--hud-blue:       #1f6f94;  /* teal-cyan mid HUD — CMYK 85 45 25 10 */

/* Print substrate — neutral-cool greys since 2026-05-24, not warm cream */
--bg:             #c8c5bf;  /* ash-concrete — the brick wall (page background) */
--paper-cream:    #f0eee9;  /* light industrial flyer-stock — primary card surface */
--paper-light:    #e2ded7;  /* slightly darker grey alternate surface */
--paper-aged:     #c8c2b8;  /* weathered grey — decay register */

/* Ink scale — warm sepia drift, not neutral gray */
--ink:            #1a1512;  /* near-black with red bias — riso warm black */
--ink-dark:       #2b231d;  /* warmer secondary heading weight */
--ink-smoke:      #4d4339;  /* sepia mid-tone — body emphasis */
--ink-dust:       #665b4e;  /* muted labels, subtitles */
```

These are the live values in `dc-palette.css` — that file, not this document, is the
source of truth for token values. `dc-palette.css` also carries tokens omitted above
(`--concrete-pale`, `--paper-stain`, `--orange-deep`, `--ink-mid`, `--deep-rust`,
`--amber-dark`, the `--brand-*` signature layer); consult it before adding a color.

Color token names are semantic — `--blood` is not "dark red", it is the specific
heading-level red chosen because `--crimson` fails WCAG AA contrast (2.71:1) against
the page background `--bg` while `--blood` reaches 5.21:1. That constraint is baked
into the token name, not scattered across heading rules.

### Typography Tokens

```css
/* Type families — named by role, not by font name */
--font-display:  'lixdu', 'Tomorrow', sans-serif;
--font-body:     'Titillium Web', Georgia, sans-serif;
--font-mono:     'Tomorrow', 'Titillium Web', monospace;

/* Type scale — physical units, 12pt body floor */
--fs-body:    12pt;
--fs-body-sm: 11pt;    /* design floor — never go below this for prose */
--fs-body-xs: 11.5pt;  /* between sm and body — outcome text, cover body, TOC items */
--fs-footer:  9.5pt;   /* @page margin-box footer text */

/* Line height */
--lh-normal:  1.5;
--lh-tight:   1.35;

/* Letter spacing — named by use */
--ls-display:  0.1em;   /* all-caps display headings */
--ls-cap-sm:   3px;     /* mono micro-caps (.tag, .dc-tag) */
```

### Spacing and Geometry Tokens

```css
/* Spacing — physical units */
--space-sm:  0.08in;
--space-md:  0.12in;
--space-lg:  0.15in;
--space-xl:  0.20in;
--gutter:    0.15in;    /* column gap, structural section margins */
--space-2xl: 0.25in;    /* spacing-scale step; do not substitute for --gutter */

/* Page geometry — must match @page size declaration exactly */
--page-width:     8.625in;
--page-height:    11.25in;
--page-margin:    0.5in;
--binding-margin: 0.75in;  /* spine-side in @page :left/:right */
```

### Page Background and the Viewer

The page background is declared on `@page`, and nowhere else. One `@page` rule
paints the entire sheet — the content box, and every margin box that generates
no content of its own shows it through — so there is no wrapper element to
style and no viewer hook token. The color and the texture are two declarations
in two files:

```css
/* page-rules.css — the base color */
@page { background-color: var(--bg); }

/* dc-native.css — the brick tile over it */
@page {
  background: var(--bg) url("../images/brick-bg-01.png") repeat;
  background-size: 1.5in auto;
  background-blend-mode: multiply;
}
```

**The `url()` must be local and repo-relative.** The build stages every image
your project stylesheets reference and emits one `<link rel="preload"
as="image">` for it, which is the second reference Chromium needs before it
will paint a page background at all. A remote `url(https://…)` is never staged,
so it is never preloaded, and the sheet prints the background *color* alone —
silently. `gutterpress build` reports that shape as
`engine.page-background.unreferenced`. The staged-and-preloaded asset pipeline
that makes this shape work landed in Gutterpress 0.10.2-alpha.1.

To change the page background in an adapted project, override `--bg` in
the book's own sheet (`@layer book`); the `@page` rules read it directly.

### What Makes a Good Token

**Good — `--ls-cap-sm`**: Used in five rules across three files. Semantically distinct
(letter-spacing for micro-cap labels). Has no alias.

**Good — `--gutter`**: The column gap appears in grid declarations and structural
margins. One change reflows all of them without changing the spacing scale.

**Anti-pattern — removed `--secondary-color`**: Was a 1:1 alias of `--crimson` with
no additional meaning. All eight consumers were updated to `var(--crimson)` directly.
Aliases that add no semantic distinction split the refactoring surface without buying
readability.

**Anti-pattern — alias with wrong fallback**: `--accent-color1: var(--hud-blue,
#ff6a3d)` — the fallback `#ff6a3d` is bright orange, the opposite of HUD blue. Wrong
fallbacks silently corrupt rendering when the primary token fails to resolve. All
fallbacks must match the canonical token's value family.

---

## 4. Page Template System

Page layout is controlled through two independent axes. Neither axis alone is
sufficient — a page needs both a geometry declaration and a content layout declaration.
Separating them into two distinct layers eliminates the specificity fights that follow
when both are merged.

### Axis 1 — `@page` Named Pages (`page-rules.css`)

`@page` rules own geometry: page size, margin sizes, running headers and footers.
Named pages are declared in `page-rules.css`, and a corresponding element rule assigns
a CSS class to that named page in the same file:

```css
/* page-rules.css — geometry and named-page assignment together */
@page chapter-start {
  /* Footer suppression — the named block wins on the page selector alone */
  @bottom-left  { content: none; }
  @bottom-right { content: none; }
}

@page chapter-start:left {
  margin-right: var(--binding-margin, 0.75in);
  margin-left:  var(--page-margin);
}

@page chapter-start:right {
  margin-left:  var(--binding-margin, 0.75in);
  margin-right: var(--page-margin);
}

/* Named-page assignment — lives adjacent to its @page declaration */
.dc-chapter-start { page: chapter-start; }
```

Named pages in this codebase: `chapter-start`, `chapter-end`, `front-matter`, `full`,
`citizen-file`, `clean`. `chapter-end` is declared only — no markdown source in this
repo carries `.chapter-end`. `@page :blank` styles blank pages the fragmenter
inserts — use it to suppress footers on them.

### Axis 2 — Content Layout Selectors

While `@page` controls the physical box, `.page.*` selectors control what happens
inside it: column count, column-fill strategy, break behavior. Those selectors live
in the design guide's own sheet. The `.page` class is the structural hook;
specialized classes extend it:

```css
/* shared or guide-owned content layout */

/* Two-column rules pages. The COUNT is Gutterpress core's
   (`.gp-columns-2` in GUTTERPRESS_CSS) — the theme may not redefine
   `columns` on it. What the theme sets is the gap (page-templates.css,
   through core's `--gp-column-gap` hook) and the fill strategy for this
   shape (dc-native.css §10b: a `.page` is one sheet, so its run
   does not fragment and `balance` is correct). */
.page.gp-columns-2 {
  column-fill: balance;
}

/* Full-bleed art pages */
.page.dc-full-page {
  width:  var(--page-width, 8.625in);
  height: var(--page-height, 11.25in);
  break-before: page;
  page-break-before: always;
}
```

The double-class pattern (`.page.dc-chapter-start`, `.page.page-toc`) is intentional:
`.page` provides the base reset; the second class carries the page-type identity.
Specificity (0,2,0) beats single-class overrides from upstream CSS without
`!important`.

Guide-only examples should live in the design guide's own sheet even when they use `.page.*`
selectors.

### Folios and the `.chapter-N` class

**Folios use the built-in `page` counter and nothing else.** `page-rules.css`'s
`@page :left` / `:right` margin boxes emit `"P." counter(page)` on the outer
corner. There is no `counter-reset` for it anywhere in `dc-design-guide/css/`,
so page numbers run continuously from the first page of the book — front matter
included. A book wanting body folios to restart at 1 would have to add that
reset; none does today.

**There is no chapter counter.** The `C.N` chapter chip is a GCPM *string*, not
a counter — see the next section. `counter(chapter)` resolves to nothing,
because nothing defines it.

**`.chapter-N` is a styling hook, not a counting one.** `markers.js` stamps it
onto every `@page` opened inside an `@chapter … ch="N"` (its `counterClass`
merge), so authors never hand-apply it. Its only consumers are positional
overrides in a book's own sheet — e.g. `.page.dc-chapter-start.chapter-03 …` for
that chapter's opener art. No rule in any sheet uses it for a counter.

### Chapter Footer Labels — `string-set` / `string()`

The producer is one rule at the bottom of `page-rules.css`:

```css
div.chapter[data-ch] { string-set: guideSection attr(data-ch); }
```

and the consumers are the generic `@page :left` / `@page :right` bottom margin
boxes in `page-rules.css`, which emit `"C." string(guideSection, first)`.

One constraint on the producer: write `ch="N"` in the `@chapter` directive, not
`data-ch="N"` — `markers.js`'s `attachDataAttrs()` already prefixes unknown keys
with `data-`.

Verified end-to-end on this guide: a `build --format pdf` of `dc-design-guide`
yields footers `C.1` ×58, `C.2` ×57, `C.3` ×36, `C.4` ×5, `C.5` ×6, `C.6` ×4 —
matching the chapter sizes.

### TOC Page Numbers — `target-counter()`

`target-counter()` gives automatic cross-reference page numbers:

```css
/* shared content layer */
.dc-toc ol > li > a::after {
  content: target-counter(attr(href), page);
}
```

`target-counter()` resolves the `href` anchor to find its target element and inserts
that element's page number at render time.

---

## 5. Markdown-Friendly Selectors

Markdown generates clean HTML with minimal class names. A paragraph is a `<p>`. A
heading is an `<h3>`. Authors should not need `{.class}` on every element — CSS does
the targeting work by anchoring selectors to structural containers that markdown's own
output reliably provides.

### Strategy 1 — Child Combinator + Element Type

When content lives inside a container with a known class, the child combinator targets
elements without requiring authors to add classes:

```css
/* a book's own sheet — first h1 in every @chapter wrapper triggers a page break */
div.chapter > h1:first-of-type {
  break-before: page;
  page-break-before: always;
}

/* The inverse — non-title h1s (specimens) do NOT page-break */
div.chapter > h1:not(:first-of-type) {
  break-before: auto;
  page-break-before: auto;
}
```

The structural anchor also lets you selectively opt elements out of a behavior without
touching the markdown.

### Strategy 2 — `:first-of-type`, `:only-child`, and Adjacent Sibling

These pseudo-classes target positional relationships that correspond to authoring
conventions. The gear entry tagline is always an italic paragraph immediately after
an h3:

```css
/* the shape of the pattern — the gear rules that carried it were removed
   2026-08-21 (they keyed on classes nothing emits; see components/data.css) */
.dc-card.dc-gear > p:first-of-type em:only-child,
.dc-card.dc-gear > p.dc-flavor:first-of-type {
  font-style: italic;
  font-size: var(--fs-body-sm);
  color: var(--ink-smoke);
  display: block;
}
```

The author writes `*Melee. Cyberware implant. Pair.*`. Markdown renders
`<p><em>…</em></p>`. The selector targets the `<em>` that is the only child of the
first paragraph. If any text falls outside the asterisks, the structural selector
silently fails. An explicit escape-hatch class is the usual remedy; the gear
component no longer ships one, since its rules were removed as unreachable.

The adjacent sibling prevents headings from stranding without content:

```css
/* the design guide's own sheet (@layer book) */
div.chapter h2 + p, div.chapter h3 + p {
  break-before: avoid;
  page-break-before: avoid;
}
```

### Strategy 3 — Container Context Scoping

The `div.chapter` and `.page.*` parent selectors scope rules to their context.
A rule scoped to `section#ch-name` is guaranteed not to bleed into adjacent chapters:

```css
/* the design guide's own sheet (@layer book) */
.page.page-credits.dc-credits > h1,
.page.page-intro.dg-intro > h1,
.page.page-chapter-start.dc-chapter-start > h1 {
  color: var(--paper-cream);
  background: var(--rust);
  clip-path: var(--clip-banner);
}
```

The triple-class specificity ensures this wins without `!important`.

### Strategy 4 — Wrapper Containers and the `@macro` Pattern

The design guide uses `@macros` exclusively — `:::` container syntax has been removed
from all design guide source files. When a macro like `@definition` emits a wrapper
`<div class="dc-definition-block">`, target children by element type without requiring
authors to annotate every element:

```css
/* components/data.css — children addressed by type, not by class */
.dc-definition-block {
  background: var(--surface-orange-tint);
  border-left: 4px solid var(--crimson);
  padding: 10px 14px;
  font-style: italic;
}

.dc-definition-block p     { margin: 0; }
.dc-definition-block p + p { margin-top: 6pt; }
```

The macro author writes:

```markdown
@definition
Augmercs are muscle for hire.

@end-definition
```

No `.dc-definition-block-paragraph` class is needed. The `p + p` selector handles
multi-paragraph definitions automatically.

> **Note on `:::` containers:** REMOVED. The `:::wrapper {.class}`, `:::sidebar`,
> `:::callout` forms were deleted from print-md core on 2026-05-17 (see the comment
> in `packages/cli/src/lib/markdown/renderer.ts`). They no longer parse — any
> remaining `:::` in a source file renders as literal text. The `@macro` family is
> the only container surface. See the migration table in
> `dc-design-guide/README.md` for the old → new mapping.

When two prose-box components genuinely share the same shell behavior, give them a
real base class and emit it in markup. In the dc-design-guide, `@definition` and
`@sidebar-box` can share a tiny `.dc-prose-panel` shell for common padding/margin/
break behavior, while `.dc-definition-block` and `.dc-sidebar-box` keep their own
surface, accent, heading, and text rules. Do not use that base for unrelated inset
layout components like `.dc-sidebar`.

**Anti-pattern:**

```css
/* Don't do this — forces authors to annotate every element */
.dc-definition-block-text  { font-style: italic; }
.dc-definition-block-intro { margin-top: 6pt; }
```

### Strategy 5 — The `@chapter` Macro as CSS Hook

`@chapter #ch-name .page-class` at the top of a markdown file generates:

```html
<div class="chapter ch-name page-class" id="ch-name">
```

Note: the id slug is also added to the class list. This gives two independent CSS
handles:

```css
/* By chapter ID — applies only to this chapter */
#ch-toc h1:first-of-type { break-before: auto; }

/* By page class — applies to pages of this type */
.page.fg-components > h2 { color: var(--blood); }
```

Use the ID form for chapter-specific exceptions. Use the class form for page-type
conventions that should apply consistently across the book.

### Strategy 6 — When You DO Need a Class

A class is necessary when the same element type serves multiple structural roles at
the same DOM depth inside the same container. If a component needs to distinguish
between a primary `h3` (item name) and a secondary `h3` (subsection), position alone
cannot separate them. That is the correct moment to add `{.classname}` to the
markdown element.

The escape hatch is `{.classname}` on the markdown element. Raw HTML is a last
resort, permitted only when markdown cannot produce the required semantic structure.
Document any raw HTML exception explicitly in the component's documentation.

The `:has()` relational pseudo-class enables parent-aware targeting — for example,
`li:has(> strong:first-child)` styles list items whose first child is bold. Use it
when structural selectors alone cannot express the relationship.

---

## 6. CSS Nesting for Component Scoping

Chromium has full support for native CSS nesting. Component
rules can be written with explicit parent-child scope rather than long compound
selectors:

```css
/* Without nesting — relationships implied by shared prefix only */
.dc-sidebar-box { background: var(--paper-cream); padding: 14px 18px; … }
.dc-sidebar-box > h4:first-child { font-family: var(--font-display); … }
.dc-sidebar-box hr { border-top: 1px dashed var(--blood); … }
.dc-sidebar-box p { font-size: var(--fs-body-sm); … }

/* With nesting — scope is structurally enforced by the parser */
.dc-sidebar-box {
  background: var(--paper-cream);
  border: 1.5px solid var(--border-hairline);
  border-left: 4px solid var(--blood);
  padding: 14px 18px;
  margin: 0.15in 0;
  break-inside: avoid;
  page-break-inside: avoid;

  & > h3:first-child,
  & > h4:first-child {
    font-family: var(--font-display);
    font-size: var(--fs-h4);
    font-style: italic;
    color: var(--blood);
    text-transform: uppercase;
    margin: 0 0 10px;
  }

  & hr {
    border: none;
    border-top: 1px dashed var(--blood);
    margin: 7.5pt 0;
  }

  & p             { margin: 0; font-size: var(--fs-body-sm); line-height: var(--lh-normal); }
  & p + p         { margin-top: 6pt; }
}
```

The `&` operator refers to the parent selector. `& > h4:first-child` compiles to
`.dc-sidebar-box > h4:first-child`.

### When Not to Nest

Nest for direct parent-child and immediate-sibling relationships within one component
boundary. Do not nest to mirror DOM structure across multiple levels — every nesting
level increases compiled-selector specificity and makes future overrides harder.

The specialty density overrides stay flat deliberately:

```css
/* shared print-density layer — flat, not nested chains */
.specialty .dc-learning-path       { page-break-before: always; }
.specialty .dc-learning-path h3    { padding-top: 0.06in; }
.specialty .dc-learning-path .dc-intro { font-size: 0.65rem; }
```

Nesting these would imply a DOM hierarchy between `h3` and `.dc-intro` that does not
exist.

---

## 7. Break and Pagination Control

Page breaks are the most common source of layout regressions.

### Always Pair Break Properties

`break-inside: avoid` is the spec-compliant property and the one that governs the
print output. The sheets in this project pair it with the legacy
`page-break-inside: avoid` alias throughout; keep new rules consistent with that:

```css
.dc-callout,
.dc-stat-block,
.dc-card.dc-gear {
  break-inside: avoid;
  page-break-inside: avoid;
}
```

The same pairing applies to `break-after`/`page-break-after` and
`break-before`/`page-break-before`.

### `break-before: page` vs `break-before: always`

These are not equivalent in multi-column layouts. `break-before: always` forces a
break out of any fragmentation context — including columns — which produces an
unexpected column break rather than a page break in two-column sections.
`break-before: page` is specific to page fragmentation and is the correct choice in
column contexts. Pair both for full compatibility:

```css
/* Correct — page break only, not column break */
.dc-chapter-start {
  break-before: page;
  page-break-before: always;
}
```

### Keep Headings With Their Content

```css
/* the design guide's own sheet (@layer book) */
div.chapter h2, div.chapter h3, div.chapter h4 {
  break-after: avoid;
  break-before: auto;
  break-inside: avoid;
  page-break-after: avoid;
  page-break-before: auto;
  page-break-inside: avoid;
}

div.chapter h2 + p, div.chapter h2 + ul,
div.chapter h3 + p, div.chapter h3 + ul,
div.chapter h4 + p, div.chapter h4 + ul {
  break-before: avoid;
  page-break-before: avoid;
}
```

### Orphans and Widows

```css
/* shared content baseline */
.page p {
  orphans: 4;
  widows: 4;
}
```

Four lines minimum at the bottom of a column (orphan) or top of the next column
(widow). This is the design guide setting; the CSS Paged Media spec default is 2.

### Tail-Row Guard Pattern

Prevent the second-to-last item in a list from being stranded without its final
sibling:

```css
/* shared print-density layer */
.dc-skill-card .dc-card-body .dc-ability:nth-last-of-type(2):not(:only-of-type) {
  break-after: avoid;
  page-break-after: avoid;
}

.dc-skill-card .dc-card-body .dc-ability:last-of-type:not(:only-of-type) {
  break-before: avoid;
  page-break-before: avoid;
}
```

The two rules work together: the second-to-last item refuses to be last on a page;
the last item refuses to be first on a new page. `:not(:only-of-type)` prevents
activation when only one item exists.

### The `.gp-no-break` Utility

For one-off elements that must not split across pages without having a component
class. This is **core Gutterpress vocabulary** (gutterpress#225) — the book no
longer defines it, so there is nothing here to copy:

Apply via `{.gp-no-break}` on a markdown element, or wrap a block with
`@section .gp-no-break` … `@end-section`.

Core ships two siblings on the same footing: `.gp-break-before` starts a new
page, and `.gp-columns-all` spans a multi-column run. Misspell any of them and
the build says so by name rather than rendering a silent no-op.

> This replaced the book-local `.pmd-no-break` at the 0.10.6 cutover. `.pmd-*`
> was converted, never aliased, so the old names are gone rather than
> deprecated.
