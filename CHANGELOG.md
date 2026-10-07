# Changelog

All notable changes to gp-dimm-city are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/) and the project uses
[Semantic Versioning](https://semver.org/). The release workflow refuses to
cut a version that has no `## [X.Y.Z]` heading below.

## [Unreleased]

### Added

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
