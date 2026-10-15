# dc-design-guide — CSS Architecture & Patterns

This document defines the CSS authoring conventions for the dc-design-guide and any
project that adapts it. It is the normative reference for all structural decisions —
when in doubt, consult this document before touching the source files.

---

## 1. Print-First Philosophy

This is a print document system. There are no `@media screen` rules, no responsive
breakpoints, no hover states. The output medium is a PDF paginated by Chromium's own
native print engine, and every rule must survive that pipeline unchanged.

**Physical units for the page, `px` for components.** Page geometry (margins, page and column sizes, gutters) and type use `pt` or `in`, which map directly to physical paper. `px` is used widely for component geometry: borders, paddings, tab labels, icon badges, stat-cell keys (`--bw-thin: 1px`, `10px 14px` callout padding), where a fixed CSS length reads consistently at any print zoom. Avoid `em` for layout
geometry (column widths, gutters, card padding) — use `0.25in` not `1.5em`. The
exception is typographic rhythm: heading margins and padding that should scale
proportionally with the heading's own font-size (`h1, h2, h3 { margin: 1.5em 0 0.5em }`)
are correctly expressed in `em`. Bullet gaps and inline padding on `code` elements are
also correct uses of `em`. The rule is about column geometry, not typographic spacing.

**The design guide is the canonical test bed.** If you are unsure how a rule renders,
add a specimen to the design guide's own sheet and build a preview.

---

## 2. The CSS Layer Stack

The stylesheet cascade is a set of files, each wrapped in one CSS **cascade
layer** (`@layer`, adopted dc#54), loaded in the explicit order of
`package.json`'s `gutterpress.styles` array. No file imports another; the
manifest array is the only place the order is written down.

**Package boundary.** This whole repository is the Gutterpress extension
package `gp-dimm-city`. A book installs it with `gutterpress ext add
gp-dimm-city` (or from the app's Features panel), which pins the exact
version and vendors a copy under the book's `plugins/npm/`. Gutterpress
≥0.11.0 wraps every extension's CSS in its own cascade layer, `@layer
ext.<name>` (this package is `ext.gp-dimm-city`), in `extensions:` list
order — so the cascade a consuming book gets is core (layered) → each
extension in its own layer, this package's seventeen sheets among them in
`gutterpress.styles` order → the book's own `styles:` last, which stay
UNLAYERED (gutterpress#265, gutterpress#227). Anything a single book needs —
a design guide's demo scaffolding, a field guide's chapter-specific art —
lives in that book's own sheet, plain and unlayered, never in this package:
being unlayered, it beats every rule in `ext.gp-dimm-city` at any
specificity, with no layer of its own required.

The layer names and order for this package's OWN sheets are declared
**once**, as a statement in `dc-fonts.css` — the first sheet the cascade
sees — so layer order never depends on file order. These are sublayers
nested inside the engine's `ext.gp-dimm-city` wrapper, not top-level layers:

```css
/* styles/dc-fonts.css — before any rule */
@layer dc.tokens, dc.base, dc.components, dc.templates, dc.pages;
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
"styles/components/entries.css",              // @layer dc.components
"styles/components/section.css",              // @layer dc.components
"styles/page-templates.css",                  // @layer dc.templates
"styles/page-rules.css",                      // @layer dc.pages
"styles/dc-native.css"                        // UNLAYERED, last — see below
```

There is no `book` entry in this statement. Before Gutterpress 0.11.0, a
consuming book joined a `book` layer declared here to win cross-layer ties
without a specificity fight. Now that this whole package sits inside the
engine's `ext.gp-dimm-city` wrapper, that sublayer would only be reachable
from *inside* this package — a book's separate `styles:` sheet can't nest
into it — so it was dead weight nobody could target, and it has been
dropped. A book needs no replacement for it: its `styles:` sheets are
unlayered by the engine and already win every cross-layer tie against this
whole package, at any specificity, without joining any layer at all.

**Two sheets are deliberately UNLAYERED — within this package.**
`dc-native.css` is the last entry in the array and carries the
engine-specific native-print chrome (margin-box chip styling, the brick
margin band, native-print break fixes). Unlayered CSS always outranks
layered CSS, no matter which layer, no matter specificity — that is the ONE
piece of the cascade stronger than any `@layer` — so within
`ext.gp-dimm-city`, it beats every `dc.*` sublayer, which is why it must
stay last in the array. From outside the package, though, `dc-native.css` is
just part of the single `ext.gp-dimm-city` layer like everything else here —
the book's own `styles:` sheets beat it automatically, at any specificity,
the same way they beat every other sheet in this package, with no
unlayered-sheet trick required. `dc-fonts.css` is the other unlayered file,
for an unrelated reason: it carries the `@layer` statement (which must be a
top-level statement relative to this package's own sublayers, not nested
inside one of them) and its only rules are `@font-face`, where a layer would
be pointless — font-family lookup is not a cascade contest.

### Layer Responsibilities

| Layer | Files | Owns | Must NOT contain |
|---|---|---|---|
| `dc.tokens` | `dc-palette.css`, `dc-identity.css`, `dc-component-defaults.css` | `:root` token blocks (palette primitives, specialty-identity aliases, component public-token defaults) | `@page` rules, `.dc-*` components, `.page.*` layout rules, html/body baseline |
| `dc.base` | `dc-core.css` | html/body baseline, global element resets, heading defaults, `* { print-color-adjust }` | `@page` rules, `.dc-*` components, `.page.*` layout rules |
| `dc.components` | `components/{callouts,specialty-identity,chrome,cards,specialty,data,images,entries,section}.css` | Every `.dc-*` component class (base + token contracts + thin variants), specialty parent-container overrides, and the section variants (`.dc-section-panel`, `-flat`, `-aside` and the section components, all in `section.css`) | any column layout (`columns`, `column-count`, `column-gap`, `column-fill`, `column-rule`), `@page` declarations, `div.chapter` scaffolding |
| `dc.templates` | `page-templates.css` | `.page.*` content layout including the front-matter pages every Dimm City book writes (contents, credits, chapter start), the location rules for the page and chapter words (tokens only), page wrapper scaffolding, print utilities, `.dc-specialty` break control | `@page` declarations, `.dc-*` component styles, `:root` tokens, any column layout |
| `dc.pages` | `page-rules.css` | Every `@page` declaration, named-page geometry, margin-box content (folio + chapter footers), the `string-set` producer for the chapter footer label | Component styles, token definitions, column layout |
| *(unlayered, within this package)* | `dc-fonts.css`, `dc-native.css` | `@font-face` and the `@layer` statement (`dc-fonts.css`); engine-specific native-print chrome that must beat every `dc.*` sublayer (`dc-native.css`) | Anything that should lose to the book's own `styles:` — every sheet here sits inside `ext.gp-dimm-city`, which the book's unlayered sheets always outrank |

### Sections and locations

Two kinds of word sit on the structural markers, and each has one home.

A **section variant** is a word on `@section` (`@section panel`, `flat`, `reference`, `lore`, `dm`, `choose`, or a component word such as `npc`). The plugin declares it in `plugin.js` (`markers.section.variants`), core resolves it to a class, and the look is that class's rule. A **location** is a word on `@page` (`chapter-start`, `intro`, `credits`, `contents`, `citizen-file`) or on `@chapter` (`rules`, `lore`, `citizen-file`, `specialty`); it resolves to `dc-page-<word>` or `dc-chapter-<word>`, and it re-tunes the components inside it. A location never draws a component.

| What | Lives in | Layer |
|---|---|---|
| Entry cards (`.dc-entry` and its five kinds), fields (`.dc-field`) and the catalog section (`.dc-catalog`): one file, one concern | `components/entries.css` | `dc.components` |
| Section variants: chrome and the rules that style them (`.dc-section-panel`, `.dc-section-flat`, `.dc-section-reference`, `.dc-section-lore`, `.dc-section-dm`, `.dc-section-choose`, `.dc-npc-stat`, `.dc-fiction-excerpt`, …) | `components/section.css` | `dc.components` |
| Locations: what a page or chapter word changes | `page-templates.css` | `dc.templates` |
| The named page a page word selects, and its margin boxes | `page-rules.css` | `dc.pages` |
| Token defaults for every public `--dc-section-*` knob (and every other component token) | `dc-component-defaults.css` | `dc.tokens` |

Two rules keep the split honest, and a test enforces each:

- **No plugin rule on a bare `.section`.** A bare `@section` is core's plain box and splits across pages. Chrome lives on a variant class, so no selector in `styles/**` may match `.section` without a `dc-` class on the same element. Enforced by `test/conventions.test.js`: *a bare @section is unstyled > no selector in styles/\*\* matches `.section` without a dc- class on the same element*.
- **Location rules set tokens only.** A rule keyed on a page or chapter class may style its own element (the page's margins, its `h1`) and plain elements (`p`, `li`, `strong`), but on a component it declares custom properties and nothing else: never `background`, `box-shadow`, `padding`, `clip-path` or a pseudo-element. The component's own rule reads the token. Enforced by `test/conventions.test.js`: *a location adjusts components by tokens only > a rule keyed on a page or chapter class declares only custom properties on a component*.

```css
/* page-templates.css — the chapter-start page re-tunes the excerpt; it does not draw it */
.page.dc-page-chapter-start .dc-fiction-excerpt {
  --dc-fiction-depth: 10px;
}
```

A book overrides a location the same way, with the same selector shape in its own sheet (`.page.dc-page-chapter-start .dc-fiction-excerpt { --dc-fiction-depth: … }`). It never invents a page class of its own. Which words exist, and which entry in `components.yaml` and which snippet covers each, is checked by `test/integrity.test.js` (*component catalog*).

### Column Ownership Rule

**This package owns no column layout.** There is one way to put content in
columns, and it is Gutterpress core's: `@columns N` … `@column-break` …
`@end-columns` (N from 1 to 5). Everything between the markers is in that many
columns. Core ships the classes it emits (`.gp-columns`, `.gp-columns-N`) in
`GUTTERPRESS_CSS`, and a theme may not define competing generic names or
re-declare any column property on them (gutterpress `CLAUDE.md` §6). This
theme used to ship `.two-column` / `.three-column`, then per-component column
forms (`@card-grid`'s own `columns`, a skill card's `.dc-two-col`, the credits
`.dc-colophon-grid`, the `---{.column-break}` rule, the `.dc-at-a-glance-cards`
grid); they are all gone, and a component that wants columns says so in
markdown: `@columns 2` inside `@skill`, `@card-grid`, `@npc-stat`,
`@citizen-walkthrough`, or around the colophon names.

So no stylesheet sets `columns`, `column-count`, `column-width`, `column-gap`,
`column-fill` or `column-rule` (`test/integrity.test.js` enforces it). What the
package says about a column run is two author hooks, set **once**, at `:root`
in `dc-component-defaults.css`, with no column selector:

| Hook | Value | A component that wants none |
|---|---|---|
| `--gp-column-gap` | `var(--gutter)` | — |
| `--gp-column-rule` | `1pt solid var(--border-hairline)` | `--gp-column-rule: none` (`.dc-card-grid`, the credits colophon) |

`--gp-column-rule` needs a Gutterpress that reads it; older ones ignore it and
draw no hairline. `column-fill` is not set anywhere: `balance` is the CSS
initial value, and core has no sequential-fill opt-in.

What the package still owns around a run:

| Concern | Owner | Selector |
|---|---|---|
| How many columns, the gap, the rule, the fill | Gutterpress core | `@columns N` |
| Components reacting to sitting inside a run (a `.dc-alert` may fragment; an `@npc-stat`'s entries break between creatures; a walkthrough's `h4` keeps a two-line height) | `dc-native.css` §5, `components/section.css` | rules keyed on the run: `:is(.gp-columns, [class*="gp-columns-"])` or `.gp-columns` |
| Grids inside ONE component (not column layout) | `components/data.css` | `.dc-stat-grid`, `.dc-steps`, `.dc-outcome-row` |

A column run is `@columns 2`; a card around one is a `@section panel` with the
run inside it, so the heading bar sits full width above the columns.

### Layer Contract Rules

**Tokens flow downward only.** The `:root` block is the exclusive property of
the `dc.tokens` layer (`dc-palette.css`, `dc-identity.css`,
`dc-component-defaults.css`). No other layer defines custom properties on
`:root`. All layers consume tokens via `var(--token)`. A book's own `styles:`
sheet — unlayered, so it beats this whole package regardless — is the only
sanctioned override path; do not edit the `dc.tokens` files for
project-specific changes.

**No upward `!important` fights.** Layers do not override each other with
`!important`, and a layer-order flip is never fixed with `!important` either
— see "Cascade layers, not just file order" below. Margin-box content is
plain `@page` cascade: one block per named page wins on the page selector
alone (see `page-rules.css`'s "ONE BLOCK PER NAMED PAGE" contract).

**Selector ownership is exclusive.** If you are writing a rule for `.dc-alert`, it
belongs in `components/callouts.css` (`@layer dc.components`). If you are writing
an `@page` rule — including the page background — it belongs in `page-rules.css`
(`@layer dc.pages`). If you are writing a selector that only exists for a rendered
design-guide example, it belongs in the design guide's own sheet.
A `.dc-*` selector in `page-rules.css` is a bug.

**Cascade layers, not just file order (dc#54).** Layer order decides a
cross-layer tie **regardless of selector specificity** — a one-class rule in
`dc.pages` beats a three-class rule in `dc.components`. This is what makes the
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

/* Print substrate — neutral-cool greys, not warm cream */
--bg:             #c8c5bf;  /* ash-concrete — the brick wall (page background) */
--paper-cream:    #f0eee9;  /* light industrial flyer-stock — primary card surface */
--paper-light:    #e2ded7;  /* slightly darker grey alternate surface */
--paper-aged:     #c8c2b8;  /* weathered grey — decay register */

/* Ink scale — warm sepia drift, not neutral gray */
--ink:            #1e1d1c;  /* near-black with red bias — riso warm black */
--ink-dark:       #2f2622;  /* warmer secondary heading weight */
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
--fs-floor:   10pt;    /* THE floor: no glyph is smaller (chips, tabs, labels, folios too) */
--fs-body:    12pt;
--fs-body-sm: 11pt;    /* smallest running prose in a component */
--fs-body-xs: 11.5pt;  /* between sm and body — outcome text, cover body, TOC items */

/* Line height */
--lh-normal:  1.5;
--lh-tight:   1.35;

/* Letter spacing — named by use */
--ls-display:  0.1em;   /* all-caps display headings */
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

/* dc-native.css — the brick tile over it (opaque: PDF/X-1a has no
   transparency, so the tile is pre-multiplied into --bg, no blend mode) */
@page {
  background: var(--bg) url("../images/brick-wall.png") repeat;
  background-size: 1.5in auto;
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
the book's own sheet; the `@page` rules read it directly.

### What Makes a Good Token

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
.dc-page-chapter-start { page: chapter-start; }
```

Named pages in this codebase: `chapter-start`, `front-matter`, `front-matter-intro`,
`full` and `citizen-file`. A page word selects its named page (`@page contents` and
`credits` are `front-matter`, `intro` is `front-matter-intro`). `@page :blank` styles
blank pages the fragmenter inserts — use it to suppress footers on them.

### Axis 2 — Content Layout Selectors

While `@page` controls the physical box, `.page.*` selectors control what happens
inside it: break behavior and geometry (columns are `@columns`, core's). Those selectors live
in `page-templates.css`; a guide-only specimen's live in the design guide's own sheet. The
`.page` class is the structural hook; the page word (`@page chapter-start` writes
`dc-page-chapter-start`) is the second class that names the page type:

```css
/* shared or guide-owned content layout */

/* Columns are not a page template's: a rules page sets its text in
   `@columns 2` … `@end-columns`, which is Gutterpress core's. The theme sets
   only the gap and the rule, as two tokens at :root
   (dc-component-defaults.css). */

/* Full-bleed art pages */
.page.dc-full-page {
  width:  var(--page-width, 8.625in);
  height: var(--page-height, 11.25in);
  break-before: page;
  page-break-before: always;
}
```

The double-class pattern (`.page.dc-page-chapter-start`, `.page.dc-page-contents`) is intentional:
`.page` provides the base reset; the second class carries the page-type identity.
Specificity (0,2,0) beats single-class overrides from upstream CSS without
`!important`.

Guide-only examples should live in the design guide's own sheet even when they use `.page.*`
selectors.

### Page chips: the folio, the chapter coupon and the running head

The chip **content** is `page-rules.css` (`@page :left` / `:right`); the chip
**chrome** is `dc-native.css` §2 and §2b, unlayered and last. A margin box takes
`background`, `border`, `padding`, `margin`, `height` and `vertical-align`, but no
`transform` and no `box-shadow`, so a chip's hard shadow is a thicker bottom and
right border. Three rules keep the type centred:

- the box height is fixed (16pt) rather than `fit-content`, and the engine
  centres the line in it (`vertical-align: middle; line-height: 1`); the thin top
  edge is balanced with `padding-top`, and the inline-end padding gives back the
  tracking a `letter-spacing` leaves after the last glyph;
- the chip sits in the **printable** footer band, below the text block with
  clear wall between them: the bottom margin (`--bottom-margin`) is 1in from the
  sheet edge, DriveThruRPG wants text 0.5in inside the trim (0.125in in from the
  sheet), so nothing may print below 0.625in. A 17pt chip with
  `margin-top: 0.125in` ends at 0.639in and leaves 0.125in of bare wall above it
  on every wall page. The engine honours a margin on a margin box (measured: a
  4pt margin moved the box 4.3pt). Pages without footers (`chapter-start`,
  `front-matter-intro`) set `margin-bottom: 0.75in`, which is still 0.625in from
  the trim, inside the 0.5in minimum;
- nothing clips: a chip is a plain bordered box, so no glyph can be cut.

The chapter chip's **colour** reaches a margin box through a *named page*: a
margin box is in the page context and cannot see a chapter's
`--dc-section-accent`, and a custom property set on a named `@page` does not
reach its margin boxes (measured). `page-rules.css` puts a chapter's pages on
`page: dc-chip-<hue>` (the chapter words `specialty`, `rules` and `lore` do it;
a book does the same for its own chapters with
`:where(#ch-xyz) > .page { page: dc-chip-rust; }`), and `dc-native.css` §2c
repaints the coupon for that name and side (blue, rust, violet, amethyst,
amber; the default is magenta-deep). Unlayered, because layered `@page` rules
lose to `dc-native.css`.

**The running head** is the same chip a third time, in `@bottom-center`:
the chapter's name between the folio and the chapter coupon, drawn by
`dc-native.css` §2d (paper-cream face, mono type at the 10pt floor, ink edge, hard
shadow, a rail in the chapter's colour through the same named pages). Its text is
GCPM `string-set` / `string()`, which Gutterpress resolves itself
(`stringValueAt`; `first`, `start`, `last` and `first-except` are all supported),
fed in `page-rules.css` by the chapter: `@chapter … head="…"` (`data-head`),
else the chapter's `#` title (`div.chapter:not([data-head]) > .page > h1`),
else `"Chapter " attr(data-ch)`. The string is read with `last`, so a page where a
new `#` begins names the chapter it ends in. A chapter with none of these has no
source and prints no head: do NOT seed the string with a `body` rule (an engine
string with no source falls back to a counter and prints a stray number). Every
template that clears the footer (`front-matter`, `front-matter-intro`,
`chapter-start`, `full`, `:blank`, and a book's own named page such as the
guide's `dg-doc`) clears it with `@bottom-center { content: none; }`. It sits in
the footer band and not the top, because a head at the top edge would cost every
page 0.375in of text height (0.625in to 1in) to stay inside the 0.5in text
minimum. A page name outranks `:left` / `:right`, so the named-page overrides
stay unlayered in `dc-native.css`, as for the coupon.

The Citizen File running head is the same chip in the top band (`@top-left` /
`@top-right` on `citizen-file`), hung 0.625in below the sheet top with `margin-top: calc(0.625in + 1pt)` in a 1in top margin.

### Free-standing page text

Text that is a direct child of `.page` or `.chapter` with no component around it
is dressed by `page-templates.css` ("FREE-STANDING PAGE TEXT"): `#` a banner,
`##` / `###` / `####+` paper slips, loose paragraphs, lists and quotes one
paper sheet per run. These are rules on plain elements, which a location may
style (a location styles a component by tokens only). Scope is one `:where(.page:not(.dg-doc, .dc-page-contents, .dc-page-credits), .chapter) > …`
plus a guard, `:not([class*="dc-"]…)`, that leaves any element a component has
claimed alone (`ol.dc-steps`, `div.dc-intro`, `div.dc-toc`: this layer outranks
`dc.components`; `test/page-text.test.js` enforces it), so a heading
inside a section or callout is never matched, the guide's `@page .dg-doc`
explainer pages stay plain, and `{.dc-chevron}` / `{.dc-spray}` headings keep
their own substrate. Tokens: `--dc-page-slip-bg/-ink/-edge/-shadow/-tape/-gap/-offset`,
`--dc-page-sheet-pad`, `--dc-page-title-ink`, and `--dc-heading-gap` (the space above any plain heading that follows a box) (the slip rail and the banner fill
read the chapter's `--dc-section-accent`, so a chapter word recolours them).

### Where pages break (pagination)

Break control is package CSS, so every book gets it. The rules, and where each
lives:

| Rule | File | Why |
|---|---|---|
| A panel of four blocks or fewer, with no column run or table, is `break-inside: avoid`; a long one keeps its 2nd block with its 3rd and its last block with the one above | `components/section.css` ("Where a panel may break") | no heading bar alone at a page foot, no two-line tail on its own page |
| Text in a panel or callout has `orphans: 3; widows: 3` | `components/section.css` | at 2/2 Chromium still splits a three-line paragraph 2 + 1 |
| An ability row is not glued to the block after it; only a skill card's last block stays with the one above | `components/cards.css`, `components/data.css` (the `data-ability-penultimate` / `-last` glue is gone) | a card of N rows had no place to split, so it split inside one paragraph and left a hand's breadth of empty cream |
| `.dc-dm-note > :first-child { break-before: avoid }` only inside a column run | `dc-native.css` §7 | at page level it pulled the section above's last block onto the callout's page |
| `h1`-`h6`, `.dc-tape`, `.dc-card-tab`, learning-path banners, `##` slips: `break-after: avoid` | `dc-core.css`, `page-templates.css`, `cards.css`, `data.css` | keep-with-next |
| A loose-text sheet has 3 orphans / 3 widows | `page-templates.css` | same |

What the package cannot fix is a forced `@page` / `@page-break` in a book that
strands a stub; those are content (the design guide removed three).

### The end-of-chapter mark

`page-templates.css` ("END-OF-CHAPTER MARK"): an `::after` on
`.chapter > .page:last-child`, so CSS can attach it reliably, but it cannot know
how full the page is. It is one in-flow block (`break-inside: avoid`), about
0.55in tall, not drawn on contents, credits, intro, full-bleed and art pages. A
last page that already runs to within 0.55in of its foot pushes it onto a page of
its own, so a chapter that full sets `--dc-end-mark-display: none`. It is
in flow on purpose: a plate positioned out of flow below the page's last block
lies outside the content box, which the print engine clips or answers with
whole-document shrink-to-fit. Tokens `--dc-end-mark-text/-display/-gap/-bg/-ink/-tape`.

### Folios and the `.chapter-N` class

**Folios use the built-in `page` counter and nothing else.** `page-rules.css`'s
`@page :left` / `:right` margin boxes emit `"P." counter(page)` on the outer
corner. There is no `counter-reset` for it anywhere in this package,
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
/* components/entries.css — general gear's italic tagline */
.dc-gear > p:has(> em:only-child) {
  font-size: var(--fs-body-sm);
  color: var(--ink-smoke);
  margin: 0 0 6px;
}
```

The author writes `*Melee. Cyberware implant. Pair.*`. Markdown renders
`<p><em>…</em></p>`. The selector targets a paragraph whose only child is an
`<em>`. If any text falls outside the asterisks, the structural selector
silently fails. An explicit escape-hatch class is the usual remedy.

The adjacent sibling prevents headings from stranding without content:

```css
/* the design guide's own sheet */
div.chapter h2 + p, div.chapter h3 + p {
  break-before: avoid;
  page-break-before: avoid;
}
```

### Strategy 3 — Container Context Scoping

The `div.chapter` and `.page.*` parent selectors scope rules to their context.
A rule scoped to `section#ch-name` is guaranteed not to bleed into adjacent chapters:

```css
/* the design guide's own sheet */
.page.dc-page-credits > h1,
.page.dc-page-intro > h1,
.page.dc-page-chapter-start > h1 {
  color: var(--paper-cream);
  background: var(--rust);
  clip-path: var(--clip-banner);
}
```

Two classes on the page element are enough to win without `!important`.

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

When two prose-box components genuinely share the same shell behavior, give them a
real base class and emit it in markup. `@definition` carries a tiny `.dc-prose-panel`
shell for common padding/margin/break behavior while `.dc-definition-block` keeps its
own surface, accent, heading, and text rules. Do not use that base for unrelated inset
layout components like `.dc-sidebar` (a float placement).

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

A word the plugin declares (`@chapter rules`) is not a label: it writes the class
`dc-chapter-rules`, and `page-templates.css` keys the chapter's section colour on it. Use
the word, not a class of your own, for a register the package already names.

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
.dc-note-box { background: var(--paper-cream); padding: 14px 18px; … }
.dc-note-box > h4:first-child { font-family: var(--font-display); … }
.dc-note-box hr { border-top: 1px dashed var(--blood); … }
.dc-note-box p { font-size: var(--fs-body-sm); … }

/* With nesting — scope is structurally enforced by the parser */
.dc-note-box {
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
`.dc-note-box > h4:first-child`.

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
.dc-definition-block,
.dc-card.dc-gear {
  break-inside: avoid;
  page-break-inside: avoid;
}
```

The same pairing applies to `break-after`/`page-break-after` and
`break-before`/`page-break-before`.

### Keep-whole and spacing are tokens, and the modifiers set them

Whether a box may split is one token per component, declared at `:root` in
`dc-component-defaults.css` and read by the component's own rule:
`--dc-section-break-inside`, `--dc-catalog-break-inside`,
`--dc-npc-stat-break-inside`, `--dc-skill-card-break-inside` and
`--dc-faction-break-inside` (`avoid` or `auto`). `.dc-avoid-split` is a setter of
them on the box it is written on, with `--dc-section-edge: 0px` so a whole panel
keeps its padding inside the box; it declares nothing else. A book writes the same
declarations for one box from its own sheet. No rule gives a section, a skill card
or a faction `break-inside: avoid` directly (`test/conventions.test.js`).
A catalog and a creature (an `@npc-stat` with at most one `####`) have defaults of their
own: the first splits by default (it reads `--dc-catalog-break-inside`, which
`.dc-avoid-split` also sets, so an author's override still wins), the second stays
whole.

The space under a paragraph or list item is `--dc-flow-gap`, and `.dc-snug` sets
it. It is the one token with no `:root` default, on purpose: the rule that reads
it sits in `dc.templates` so it outranks every component's own margin, and
`var(--dc-flow-gap, revert-layer)` hands the margin back to the component while
the token is unset. Declaring it at `:root` would override every component's
spacing everywhere. The "no inline fallback" rule is for the component sheets.

### `break-before: page` vs `break-before: always`

These are not equivalent in multi-column layouts. `break-before: always` forces a
break out of any fragmentation context — including columns — which produces an
unexpected column break rather than a page break in two-column sections.
`break-before: page` is specific to page fragmentation and is the correct choice in
column contexts. Pair both for full compatibility:

```css
/* Correct — page break only, not column break */
.dc-page-chapter-start {
  break-before: page;
  page-break-before: always;
}
```

### Keep Headings With Their Content

```css
/* the design guide's own sheet */
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
