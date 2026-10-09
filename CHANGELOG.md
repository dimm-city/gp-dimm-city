# Changelog

All notable changes to gp-dimm-city are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/) and the project uses
[Semantic Versioning](https://semver.org/). The release workflow refuses to
cut a version that has no `## [X.Y.Z]` heading below.

## [Unreleased]

## [1.1.5] - 2026-10-09

### Changed

- **The chapter-opener chevron rules move from `chrome.css` into the
  chapter-opener template in `page-templates.css`.** No component sheet
  selects `.chapter`/`.page` any more, and the integrity test enforces
  that with no exceptions. Pixel-identical in both books.
- `docs/cleanup-backlog.md` gains a "Still considering" section:
  - the Field Guide's sidebar areas, with the inset-rail rules;
  - the specialty-card redesign;
  - the configurable chapter prefix;
  - the offset tokens.
- `docs/css-roadmap.md` records the warnings that are known and accepted:
  - the design guide's 8 heading jumps inside component examples, which
    need an `h4`;
  - the `clip-path` and `page-containment` lint false positives, reported
    as dimm-city/gutterpress#339.

## [1.1.4] - 2026-10-09

### Changed

- **The columns contract is refined.** Page and section column layouts
  stay in `page-templates.css`. A component may lay out its own insides in
  columns in its own sheet, on a selector rooted in its `.dc-*` class (the
  two-column skill cards, the card grid). The integrity test enforces that
  rule in place of an exception list. No CSS moved.
- The integrity test's remaining exceptions are genuine hooks: the outcome
  tiers, the chapter classes gutterpress adds itself, and the design
  guide's page labels.
- `docs/css-roadmap.md` records what the CSS review left to do, and in
  which order.

### Removed

- Two unused design-guide classes: `dg-face-sample` and the
  `dc-banner-demo` section class.

## [1.1.3] - 2026-10-09

### Removed

- Distance tags: the plugin no longer turns a `Distance` table inside a skill
  into pills (`buildDistanceTags`); it now renders as a plain table. Also
  removed `.dc-distance-tags`, `.dc-dist-tag`, `.dc-dist-ap`, `.dc-dist-name`
  and the `--dc-dist-*` tokens. No book had such a table.
- Unused combinations: `.dc-flush` on `.dc-intro`, `.dc-sub-header` and
  `.dc-steps`; `.dc-intro + .dc-alert`; `.dc-card-grid > h1/h2/.dc-intro`
  (put headings and ledes outside the grid); `.section > h2.dc-h3:not(:first-child)`;
  `.dc-toc ol > li > strong`.

## [1.1.2] - 2026-10-08

**Notes for books upgrading from 1.1.1:**

- Build on gutterpress 0.11.15 or later and drop `@page .dc-printer-page`
  and your own `print.signature`: the `dtrpg` preset now does both.
- Field Guide classes that moved into the package: `.fg-snug` becomes
  `.dc-snug`, and the book-wide two-column skill cards become
  `.dc-cards-two-col` on the specialty markers.
- Section panels, padding and splitting are tokens now. A book that
  restyled `.section` chrome by overriding properties should set the
  tokens instead (see the palette reference's Section table).

### Added

- **`.dc-cards-two-col`**: on any ancestor (`@specialty`, `@chapter`,
  `@page`, `@section`), every skill card inside gets a two-column body.
  This is the Field Guide's book-wide form as an opt-in. A card's own
  `.dc-two-col`, or `.dc-allow-split`, keeps its own form.
- **`.dc-snug`**: tighter paragraph and list-item spacing on a section or
  page, for one that would otherwise overflow by a line or two (from the
  Field Guide's `.fg-snug`).
- **Split skill cards keep their lead-ins with what follows.**
  `.dc-specialty .dc-skill-card.dc-allow-split` keeps its tab, first
  blocks and lead-in paragraphs with the next block (from the Field
  Guide's own sheet).
- **Section tokens.** A section's panel, shadow and padding now come from
  tokens (`--dc-section-surface`, `--dc-section-shadow`,
  `--dc-section-pad-*`), as does whether a box may split
  (`--dc-section-break-inside`, `--dc-alert-break-inside`). Variants and
  page templates set tokens instead of cancelling properties.
- **`test/integrity.test.js`**, which checks that:
  - every class the books use is styled;
  - every token that is read, or that the palette reference documents,
    is declared;
  - each stylesheet keeps its stated contract.

### Changed

- **Tested against gutterpress 0.11.15** (stable; was 0.11.15-alpha.1).
- **CSS quick wins from an architecture review.**
  - New tokens: `--shadow-ink` (the opaque wall-shadow colour, written
    out five times before) and four exact-value `--tint-*` mix sources
    for the literal `rgb()` colours inside `color-mix()`.
  - `--dc-section-tab-overlap` and `--dc-section-tab-indent` are now
    public `:root` tokens.
  - The TOC/credits masthead `h1` is now one rule instead of two.
  - Dead declarations are gone: the `--shadow-poster` layer a specialty
    card's own `clip-path` clipped away, `page-break-inside`, an empty
    rule, a no-op height reset, three `opacity: 1`, and the
    `break-before: always` Chromium ignores on learning paths.
  - `dc-native.css` loses its tombstones and is renumbered §1–8.
  - Pixel-identical in both books, except the even specialty cards,
    whose left border is now `1.5pt` like the rest (was `1.5px`).

- **Section styling is opt-in per variant, not cancelled by a central list.**
  - `.dc-plain`, `.dc-tabbed`, `.dc-column-panel` and `.dc-card-grid` set
    the section tokens.
  - The header bar's negative margins are derived from the padding.
  - The shared page templates (intro, credits, chapter opener) own their
    styling in `page-templates.css`; the chapter opener moves there from
    `section.css`.
  - Pixel-identical in both books.
- **The credits colophon shows its 4px front-matter rail again.** A rule in
  `dc-native.css` had overridden it. This is the one visible change, on
  each book's credits page.
- **Box splitting is decided in one place.**
  - Multi-column runs and `.dc-allow-split` set the break-inside tokens.
  - This replaces an avoid → auto → avoid override chain.

### Removed

- **`.dc-printer-page` and its `@page printer-blank`** (deprecated in
  1.1.1). gutterpress 0.11.15's `dtrpg` preset pads the interior to the
  4-page signature and reserves the blank last page itself, so a book
  needs neither the marker nor its own `print.signature`. The Field
  Guide, built on 0.11.15 without either, keeps its 232 pages
  pixel-identical and still ends on four blank pages.
- `--shadow-tint`, and `.dc-roll-the-die`'s `box-shadow: var(--shadow-tint)`:
  a bare colour is not a valid shadow, so it never rendered.
- `.dc-suppress-footer` and its `@page clean` (and the design guide's
  mirror of it): no book used footer suppression.
- The design guide's dual specialist and generalist skill-tree specimens
  (Variant Gallery; The Specialty System's "One source" section, now
  "eight shapes"). Those two specialties take their skills from the other
  eight and have no trees of their own, so the specimens printed a
  generic `PATH1` sticker for something that cannot exist.

### Fixed

- The catalog's glossary entries: a glossary item is a plain paragraph
  inside `@glossary`, and no doc or gallery page writes `.dc-terms-item`
  any more, so `glossary-item-authored` is retired.

## [1.1.1] - 2026-10-08

**Notes for books upgrading from 1.1.0:**

- A learning-path banner is now an `h3` (was `h2`), and a skill's title an
  `h4` (was a `span`). A book stylesheet that targets `h2.dc-spray` or
  `span.dc-tab-title` needs the new tag.
- Unused components were removed; check `docs/cleanup-backlog.md` and the
  Removed list below before relying on any of them.
- Tested against gutterpress 0.11.15-alpha.1, whose `dtrpg` preset now
  does the DriveThruRPG blank last page and K-only black text.

### Added

- **Heading look classes `.dc-h3`–`.dc-h6`.** A heading keeps its outline
  level and takes another level's look (`## Useful Items {.dc-h3}`), so a
  book can stop skipping levels to get a smaller label: gutterpress flags
  every skip. The section header bar and the in-section accent rule follow
  the class, not the tag. On a paragraph, the class sets a line in
  heading type outside the outline. The Field Guide's 13 skipped levels
  are fixed this way and render pixel-identical. Documented in the
  design guide's Typography chapter (Level and look).

### Changed

- **Tested against gutterpress 0.11.15-alpha.1** (devDependency, was
  0.11.13), the release that upstreams this package's two DriveThruRPG
  workarounds: `preset: dtrpg` now pads to a 4-page signature and always
  ends on a blank reserved page (`print.reserveLastPage`,
  dimm-city/gutterpress#332), and prints near-black text on the black plate
  only in PDF/X builds (`pdfx.blackText: k-only`, dimm-city/gutterpress#331).
  Verified on the Field Guide with the alpha: its 228 content pages render
  pixel-identical to 0.11.13, and without any workaround the book ends on
  4 pure-white pages (232). The design guide's Publishing chapter documents
  both settings.
- **Specialty chapters nest in the outline.** A learning path's title was
  emitted as an `h2`, the same level as the specialty name, and a skill's
  title as a plain `span`, so the app's contents panel and the PDF
  bookmarks listed every skill tree beside its specialty and no skills at
  all. The plugin now emits the heading levels the markdown is written
  at: specialty (`##`) > learning path (`h3.dc-spray`) > skill
  (`h4.dc-tab-title`). The CSS follows, and both books render
  pixel-identical. A stylesheet that targeted `h2.dc-spray` or
  `span.dc-tab-title` needs the new tag. A real space
  (`span.dc-path-sep`, carrying the 10px gap the sticker's margin used to
  give) separates a banner's tree code from its title, so the outline
  reads "PRX1 Refuse Finality", not "PRX1Refuse Finality".

### Fixed

- **DriveThruRPG PDF/X builds keep live text.** The brick wall was an RGBA
  tile blended with `background-blend-mode: multiply`, so every walled page
  carried transparency, which PDF/X-1a cannot represent: Ghostscript
  flattened each one to a raster image — no live text or embedded fonts
  (a one-page book failed validation outright), and black text left
  four-colour, because `pdfx.blackText: k-only` only reaches vector text.
  The wall is now `images/brick-wall.png`, the same tile multiplied into
  `--bg` and flattened to an opaque image, painted with no blend mode:
  it renders the same (design guide wall pages differ by 0.15/255 on
  average), and with gutterpress 0.11.15-alpha.1 a DriveThruRPG build's
  body text now prints on the black plate only (separations: C = M = Y = 0
  under every glyph). A book that retints `--bg` no longer tints the
  brick; see the note in `dc-native.css` for baking a tile.
- **Nothing in the package paints transparent.** The 25 other uses of
  transparency — semi-transparent shadows, tinted fills, `opacity` on
  stickers, rules, the tape dashes and the pull-quote mark — each flattened
  their page in PDF/X-1a just as the wall did. Each is now pre-composited
  with `color-mix()` onto the surface it sits on, so it prints the same
  colour, opaque. Shadows on the wall mix against the new `--wall-tone`
  (`#c1beb8`, the tile's measured mean). Measured on both books: layout and
  page counts unchanged, and no page changes more than 0.7% of its pixels.
  The AP chip loses its soft 6px blurred shadow, which has no opaque form,
  and keeps its hard one. Every change, with where to look, is in
  `docs/print-transparency-inventory.md`. A new convention test fails on
  any transparency in the stylesheets, with no exemptions (the one
  translucent holdout, the unused cover-page composite, was removed).

- **No stray ink line across the folio row.** A skill card, learning-path
  banner or specialty intro that opened a page printed the top 2–4px of its
  outline at the foot of the PREVIOUS page: a full-width black (or accent)
  line between the folio and chapter chips. The outlines reached above
  their component's box (`top: -4px`, `translateY(-2px)`), and Chromium
  fragments that part onto the page before. Each outline now sits inside
  its own box: the card starts 4px higher and pads its tab 4px down
  (`padding-top: 4px; margin-top: -4px`), the banner 2px likewise, and
  the intro pads its content 2px. Mid-page nothing moves; a component that
  opens a page sits 2–4px lower. Measured: the line is gone from all 17 Field Guide pages and
  the 1 design guide page that had it; page counts are unchanged (232, 132) and
  no text changes page. (It became visible with 1.1.0's DriveThruRPG
  margins, which moved the page breaks; the cause dates from 1.0.0.)

- **Accent rails print as vectors in PDF/X.** The 3–5px coloured rail down
  the left of sections, ledes, path banners, the Panel and Shard blocks,
  and the front-matter and intro panels was a hard-stop
  `linear-gradient`. The PDF/X conversion turned each gradient into a
  45 ppi bitmap, so the rail's edge printed soft, and
  `gutterpress preflight` flagged the pages as low-resolution. Each rail
  is now an inset `box-shadow` over a flat fill: it looks the same and
  prints as a vector.
- **Design guide: preflight checks the right page size.** Its manifest
  declared 612 × 792 pt (the bare Letter trim), so `gutterpress preflight`
  failed every build on page size. It now declares the sheet the CSS
  prints: 621 × 810 pt, the trim plus DriveThruRPG's bleed.

- **`.gp-columns-flow` works.** Core declares it in its own layer, which
  this package's `column-fill: balance` on every `.gp-columns-2/-3`
  outranked, so a run marked to flow stayed balanced. The balance rule now
  skips runs marked `.gp-columns-flow`.

- **Catalog statuses.** `plain`, `img-float`, `full-page` and
  `printer-page` were marked `unused` although a book uses each: the
  design guide renders the first two, SysOps uses `full-page`, and the
  Field Guide still ends on `@page .dc-printer-page` until it builds on a
  stable gutterpress 0.11.15. They are `live` now.
### Removed

- `images/brick-bg-01.png`, the RGBA wall tile, is no longer published
  (it now lives in the repository's `source-art/`). Neither Dimm City book
  referenced it; a book that did should use `images/brick-wall.png`.
- **Dead styling, from an orphan audit of the package, the design guide and
  the Field Guide.** Each item was used by no book (Field Guide, Design
  Guide, SysOps), and both books render pixel-identical without it:
  - components: the cover-page composite (`.dc-cover-*`, with
    `--dc-cover-meta-border`), the contents-page rows (`.dc-toc-row/-no/
    -title/-page`), `.dc-portrait` (with `--dc-portrait-*`), the roll badges
    `.dc-roll-lucid/-surreal` (with their colour tokens), `.dc-path-subtitle`,
    the glossary item `.dc-terms .dc-item` (with `--card-border-color`),
    `.dc-dashed-rule`, `.dc-tape.dc-margin-sm`, `.dc-sidebar-box-divider`,
    `.dc-outcome-table` and `.dc-callout`. Their catalog entries are now
    `retired`.
  - rules for markup the plugin no longer produces: `.dc-sticker.active`,
    the `ol`/`li` rules under `.dc-ability` (abilities are no longer
    lists), and `h5` and `ol > li` inside a two-column skill card (both
    are converted before they get there).
  - stale comments naming deleted files or classes (`dc-tokens-print.css`,
    `components.css`, `tokens.css`, the `.pmd-*` utilities, `.dc-accent-X`,
    old design-guide chapter names, undeclared tokens).
  Styling the audit found unused but still reachable is listed in
  `docs/cleanup-backlog.md` for review.

### Deprecated

- **`@page .dc-printer-page`.** gutterpress 0.11.15+ reserves the blank
  last page in core. The class still works — a book that keeps it gets one
  printer page plus padding, still ending blank — and goes in the next
  major.

## [1.1.0] - 2026-10-07

**Layout note for books upgrading from 1.0.x:** the page margins now follow
DriveThruRPG's print specification (text at least 0.5in inside the trim),
which takes 0.25in off every page and reflows the whole book. Build and
review your book after upgrading; the Field Guide needed a short layout
pass (see `dc-op-manual`, branch `design/plugin-updates`). DriveThruRPG
books should also end with `@page .dc-printer-page` and set
`print: signature: 4` in `manifest.yaml`.

### Added

- **`@page .dc-printer-page`**, a completely blank last page (no wall, no
  footer). DriveThruRPG reserves a book's final page for printer
  information: the interior must be one page short of its signature (4 for
  US Letter) or end on a blank page. End the last chapter with this marker
  and set `print: signature: 4` in the manifest — gutterpress pads with
  blank pages to the next multiple of 4 — and the book always ends blank.
  Verified in the Field Guide (228 content pages + 4 blank = 232).
- **Variant Gallery** (design guide chapter 11): every element with more than
  one variant, its variants on one stage — all ten skill trees (each
  specialty's first learning path with one skill card, Field Guide content
  excerpted), the skill-card switches (tier override, both highlight forms,
  two columns, outcome table), every AP chip, the ten specialty intros and
  cards, class tags, alerts, blocks, choice cards, and the flush, heading,
  section, sidebar and image-float variants.
- **The design guide lives here.** `design-guide/` is the Dimm City Design
  Guide book, moved from `dimm-city/dc-op-manual`. Its manifest loads the
  package from this checkout (`extensions: - ../`), so it documents and
  renders the working copy: `npm run dev` previews it, `npm run build`
  renders the PDF, and the test suite uses it as the fixture
  (`test/design-guide.test.js`: every chapter renders clean, every macro and
  alert type is demonstrated, and each chapter's HTML is snapshotted under
  `test/__snapshots__/`). CI builds the PDF with the PR's plugin and CSS and
  uploads it; the release workflow attaches it to the GitHub release; a
  *Publish design guide* workflow deploys the HTML build to GitHub Pages.
- **`@glossary` is demonstrated** in the component gallery, which used raw
  HTML for the term-list specimen before.

### Changed

- **Page margins follow DriveThruRPG's print specification.** Its
  [Quick Specifications for Print Books](https://help.drivethrupartners.com/hc/en-us/articles/12780800178583-Quick-Specifications-for-Print-Books)
  require all text at least 0.5in inside the trim. The bleed (0.125in on
  the three outside edges, none at the spine) and the outside and binding
  margins already complied; the top did not (0.375in from the trim) and
  neither did the footer chips (0.43in). Top margin 0.5in → 0.625in on the
  sheet (0.5in from the trim); bottom 0.75in → 0.875in, as the new
  `--bottom-margin` token, so the chips print 0.55in from the trim. The
  "Citizen File" running head, which printed 0.1in from the trim, sits at
  the foot of a 0.875in top margin. Footer chips re-homed by a `.gp-flush`
  pin are top-aligned like native ones (gutterpress centres them, which put
  them 0.24in from the trim). A card title too long for its card breaks
  rather than running into the margin. **This reflows every book:** the
  Field Guide goes from 221 to 238 pages and now has no text inside 0.5in
  of the trim (it had 1,273 words on 204 pages); the design guide goes from
  126 to 131.
- **Design guide: explainer pages print plain, specimens sit on the wall.**
  Part 1 pages (and the Part 2 overview) are `@page .dg-doc`, a named page
  with a white background and neutral headings, tables and contents, so guide
  text can't be mistaken for a component. Each rendered result is wrapped in
  a framed `.dg-stage` that carries the brick wall; whole-page specimens and
  the Part 2 example pages keep the full brick page. Chapter ledes, the
  contents lists, and the explainer notes and column panels that used
  package components are now plain guide markup. All of this lives in
  `design-guide/` (markdown and `styles/guide.css`); the package is unchanged.
- **Design guide: print-design review pass.** Readability and finish fixes
  from a review against the print-quality rubrics, all in `design-guide/`:
  - Code boxes are set in IBM Plex Mono (OFL, bundled in
    `design-guide/fonts/ibm-plex-mono/`), 9pt on 1.4 leading, without the
    doubled blank lines; fences of 20+ lines may split across pages.
  - Guide text is capped at a 5.1in measure (about 65–70 characters) on 1.4
    leading; tables are 10pt and may run across pages.
  - Chapters open with a "Chapter N" label; H1 26pt, H3 13pt. Doc pages
    carry a plain running foot (folio and chapter title); the contents list
    has page numbers; Part 2 has a title page and E.1–E.6 chapter badges.
  - YOU WRITE / RESULT labels are 8pt; YOU WRITE is cream on blood (7.7:1).
  - Specimen stages stay whole unless marked `dg-tall`; prose specimens sit
    on paper (`dg-on-paper`); two Do/Don't pairs (flavor in bold italic,
    body text on bare wall).
  - Typeface specimens for lixdu, Titillium Web and Tomorrow; palette
    swatches are 1in and each carries a CMYK build from the CGATS21_CRPC1
    profile (the hand-entered four-row CMYK table is replaced).
  - Fixed: the type-scale table listed H1–H4 at stale sizes; the guide's
    inline-code style leaked into the Part 2 examples (invisible text on a
    dark callout), and its `hr` rule replaced the package's dashed rule in
    the specimen; the inset-sidebar and art-plate specimens no longer leave
    a RESULT tab stranded at a page foot.
- **Tests run against gutterpress 0.11.13** (devDependency, was 0.10.11).
- **`test/fixtures/all-macros.md` and its snapshot are gone**; the design
  guide is the fixture. `npm run test:update-snapshot` is now bun's own
  `--update-snapshots`; `scripts/update-snapshot.mjs` is removed.

### Fixed

- **No blank page after a two-column page that ends in a spanner.** A
  `@page .gp-columns-2` page ending in a full-width section printed an
  extra blank page under the DriveThruRPG margins (Field Guide: Quickstart
  vs. Deep Dive): the section's bottom margin pushed the page box past its
  one-sheet minimum. A multicol page's last child has no bottom margin.
  Design guide unchanged; Field Guide loses the blank page.
- **The introduction page keeps the normal margins.** `.page-intro` shared
  the `front-matter` named page with the Contents and Credits, whose side
  and bottom margins are zeroed for their full-bleed masthead — so the
  intro's chevron, lede and section sat flush on the sheet edge. It has its
  own named page now, `front-matter-intro`: default margins, no footers.
  The Field Guide writes its introduction as a plain `@page` and is
  unaffected.
- **No more pages printed as images.** `filter: drop-shadow()` on the
  intro page and on the labelled chapter-opener page made Chromium print
  each of those pages as one 300ppi bitmap with a soft mask: no live text,
  and a transparency mask PDF/X-1a forbids. Both shadows are vector now
  (box-shadow on the lede, section and opener badge; the opener section's
  own clipped `::after`). Design guide: 8 pages regain live text. The
  Field Guide uses neither and is unaffected.
- **No hairline across the page after the credits.** The colophon fills to
  the sheet's bottom edge, so its poster shadow's 3pt drop overflowed the
  sheet and printed as a line across the top of the next page — over the
  Field Guide's Contents masthead. The colophon keeps the shadow's side
  offset and drops the downward one. (Clipping the page was rejected: it
  would also clip a pinned or bleed plate.) Field Guide: p.2 loses the
  line, and p.1 shows the colophon's side shadow starting level with its
  top; nothing else changes.
- **Specialty art plates print full bleed.** The `.page` overflow guard
  (page-templates.css) exempted pages holding `.gp-bleed`/`.gp-pin` art but
  not `.dc-specialty-art` or `.dc-full-page`, so a plate on a page with no
  other pinned art was cut at the text column — a 100pt strip of bare wall
  down its outside edge (design guide p.45, p.105). The Field Guide's
  plates were full width only because its specialty pages also carry
  pinned art. Field Guide unchanged.
- **A long standalone banner title keeps its skew tab inside the margin.**
  `.dc-spray`'s `::before` tab overhangs its right edge by 18px; a title
  that filled its column pushed the tab past the margin, which is print
  shrink-to-fit for the whole book once the page does not clip (found by
  the build's width audit after the plate fix). Standalone banners cap at
  the column less the tab; learning-path banners, which span their shell
  with the tab pulled inside, are exempt. Field Guide unchanged.
- **A learning-path banner stays with its first card.** The shell is never
  split and keeps with the next card, and the first path after a
  specialty's art page drops its 8px top margin — moved into the package
  from the Field Guide's own sheet, which measured both. Without them the
  design guide printed the Biting Distance banner alone, with the edge of
  the first card's tab at the page foot. The package's `break-before:
  always` on `.dc-learning-path` is not a value Chromium supports and does
  nothing; it is left as is (making it valid would put every path on a new
  page). Field Guide unchanged.
- **A credits page that overflows no longer prints under the next page.**
  `.page.page-credits` had an exact one-sheet `height`; when its colophon
  did not fit, the colophon moved to a second sheet but the page box stayed
  one sheet tall, so the following page started on that same sheet and was
  painted over it (design guide: the Introduction over the colophon). It is
  a `min-height` now: a page that fits is still exactly one sheet, so the
  pinned plate still seats on the sheet edge, and the Field Guide renders
  pixel-identical. The design guide's credits example also pins its plate
  like the Field Guide's (`.gp-pin .gp-bottom .gp-full`) instead of placing
  it in the colophon, which is what had made it overflow.
- **Variable AP chips print as variable.** The plugin emitted
  `.dc-ap.variable` but the CSS only styled `.dc-ap.var`, and a `VAR AP`
  cost got no variable class at all. Both spellings are styled now, and
  `VAR` is detected alongside ranges and `X`. Visible change in the Field
  Guide: 13 pages, each a range-cost chip (`2-X AP` and the like) turning
  from standard blue to variable magenta; no layout change.
- **Short two-column runs no longer print full-page height.** `dc-native.css`
  §10b set `column-fill: auto` on every `.gp-columns-*` run; with no fixed
  height that fills the first column to the page foot, so a short column
  panel became a full-height box with an empty right column, and a heading
  above one was stranded alone when the box could not fit under it. The
  rule is `balance` again, and the two per-shape `balance` exceptions it
  made redundant are removed. A run that needs sequential fill opts in with
  core's `.gp-columns-flow`. The Field Guide's 221 pages render
  pixel-identical before and after.
- **A lede never splits** (`.dc-intro { break-inside: avoid }`), and the
  section after a lede may start a new page. Core glues every section to
  what precedes it, which chained heading → lede → section; when the section
  could not fit, the lede split and painted an empty panel to the page foot.
- **`@sidebar .inset` with a single paragraph** set that paragraph in
  centred display caps: the rail's closing-line rule matched it as the last
  child. It now applies only from the second paragraph on. The inset rail
  also keeps the sidebar's paper surface instead of a transparent one that
  put its text on the brick wall.
- Two design guide chapters (`303`, `306`) closed `@procedure` on the line
  right after a list item, which markdown folds into that item, so the
  marker never closed and the chapter rendered with a layout warning.

## [1.0.1] - 2026-09-25

### Changed

- **The layer statement drops `book`**: `dc-fonts.css` now declares `@layer
  dc.tokens, dc.base, dc.components, dc.templates, dc.pages;`. Gutterpress
  0.11.0 wraps every extension's CSS in its own cascade layer (`@layer
  ext.gp-dimm-city` for this package), so the package's own `dc.*` layers are
  now sublayers nested inside that wrapper rather than top-level layers, and
  a `book` sublayer declared here would only be reachable from inside this
  package — a consuming book's separate `styles:` sheet can't nest into it.
  Nothing in this package or any known consuming book ever put rules inside
  `@layer book`, so there is no rendered change.

### Docs

- **README quick start now requires Gutterpress 0.11.0+** and drops the
  `gutterpress ext remove ./extensions/clean-book` workaround: Gutterpress
  now layers every extension's CSS itself (in `extensions:` list order), so
  this package's rules can no longer be jumped by an unlayered starter look,
  and `gutterpress new` no longer scaffolds one anyway. The "Your own CSS"
  section no longer recommends wrapping book overrides in `@layer book` —
  a book's own `styles:` sheets are unlayered by the engine and already beat
  this whole package at any specificity.

## [1.0.0] - 2026-09-25

First release as a standalone package. Extracted from the private
`dimm-city/dc-op-manual` repository, where it lived at `dc-design-guide/` as a
folder extension that the Dimm City books referenced by relative path. The
design guide *book* stays in that repository and now consumes this package
exactly like any other book.

### Added

- **Installable from npm.** `gutterpress ext add gp-dimm-city` vendors the
  package under a book's `plugins/npm/` and pins the exact version — no Node
  packages in the book repo. `"type": "module"` in `package.json`, which the
  old folder package lacked: Gutterpress's npm loader parses a `.js` entry as
  CommonJS without it and refuses the plugin.
- **The brick-wall tile ships.** `dc-native.css` paints the page background
  from `images/brick-bg-01.png`; the old package's `files` list never included
  it, so a published copy would have failed every build with a missing asset.
  `test/package.test.js` now follows every `url()` in every stylesheet into
  the tarball.
- **Font licences.** Titillium Web and Tomorrow ship with the OFL 1.1 text
  from their upstream repositories beside the files; Lixdu ships with its own
  licence file. Fonts are grouped per family under `fonts/` with readable
  names instead of export UUIDs (byte-identical; fonts inline at build time,
  so the rename cannot change a page).
- **Snippets** for the desktop app's snippet picker: every macro an author
  reaches for (`@skill`, `@learning-path`, `@specialty`, `@callout`, `@card`,
  `@gear`, `@block`, `@outcome`, alerts, …) and the three front-matter pages
  every Dimm City book writes (contents, credits, chapter start).
- **Tests** (`bun test`): a fixture snapshot of every macro's output, the
  behavioural tests carried over from the book repo, and package checks —
  every declared path and every stylesheet asset in the tarball, one licence
  per font directory, the cascade contract below, and no runtime imports.
- **CI and release workflows**: tests on every push and PR; a manual release
  workflow that bumps, tags, publishes to npm with provenance via OIDC
  trusted publishing, and cuts the GitHub release.

### Changed

- **`css/` is `styles/`**, matching Gutterpress's extension template. Same
  sixteen sheets in the same cascade order; `tokensFile` now points at
  `styles/dc-palette.css` (the brand palette) rather than the specialty
  identity tokens.
- **The layer statement is `@layer dc.tokens, dc.base, dc.components,
  dc.templates, dc.pages, book;`** — `dc.guide` is gone. A book's own sheets
  belong in `@layer book`, the last layer, which outranks every `dc.*` layer;
  a book that must beat the unlayered `dc-native.css` lists an unlayered sheet
  after the extension. (`dc.guide` existed for the design guide's own
  scaffolding; that book now uses `book` like everyone else.)
- **Front-matter chrome moved in from the books.** The contents-page rows,
  credits role labels and prose, and chapter-start heading rules that lived
  in the design guide's sheet (`dg-overrides.css`, layer `dc.guide`) and the
  credits-page flex layout from the field guide's native sheet are now in
  `page-templates.css` and `dc-native.css`: every Dimm City book writes these
  pages. Values are carried as rendered. Two rules that only ever lost to
  them by layer order were reconciled so nothing changes on the page: the
  dead magenta TOC-divider rule (`page-templates.css`) is removed, and the
  credits role-label colour now says `--ink`, which is what it always
  rendered.
- **Specialty break control moved in from the field guide**: `.dc-specialty
  .dc-learning-path { break-before: always }` and the `.dc-allow-split`
  escape, in `page-templates.css`.
- Plugin `metadata` no longer carries its own `version` (17.3.0 in the book
  repo); `package.json` is the only version. Its `name` is now "Dimm City".
- Stale comments across the stylesheets and plugin that named files from the
  book repo (`dc-components.css`, `native-furniture.css`, `dc-tokens.css`,
  `engineStyles`, `fg-overrides.css`, `dg-overrides.css`, `index.css`) now
  name the package's own files or "the book's own sheet".

### Removed

- `index.css` (an `@import` entry point that reached into the field guide's
  folder) and `dg-overrides.css` (design-guide-only scaffolding, now that
  book's own sheet) are not part of the package.
- The catalog entries `palette-swatch` and `table`, and the `ignore:` block —
  all design-guide-only.
- The `dimm-city-components` package name.
