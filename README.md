# gp-dimm-city

The Dimm City design system for [Gutterpress](https://github.com/dimm-city/gutterpress):
the markdown-it macros, print stylesheets, design tokens, fonts and page
templates that the Dimm City TTRPG books are set in. Install it into a book
and write `@skill`, `@specialty`, `@learning-path`, `@callout` and the rest;
the package renders them and prints them.

## Install

**In the Gutterpress app:** open the book, then Project settings → Features →
*Find more on npm* (search "dimm city") or *Install from npm* and enter
`gp-dimm-city`. Confirm the install prompt. The package appears under Features
with a "+ look" badge, and its sheets and snippets are live in the preview.

**From the command line**, in the folder that holds the book:

```sh
gutterpress ext add gp-dimm-city my-book
```

Either way Gutterpress downloads the package from npm, verifies the registry
hash, writes a copy under `my-book/plugins/npm/`, and pins the exact version
in the manifest:

```yaml
extensions:
  - gp-dimm-city@1.5.0
```

**Commit the manifest, not `plugins/npm/`.** The downloaded copy is not part of
the book's history: Gutterpress adds `plugins/npm/` to the book's `.gitignore`.
The pin in the manifest is what you commit. On a fresh clone, the first build,
export or `gutterpress validate` downloads exactly the pinned version through
the same verified path (this needs the network once); after that the book works
offline.

`gutterpress ext list my-book` shows `gp-dimm-city@1.5.0 [npm; markdown, styles, components, snippets]`.

## What you get

Pick by what you are writing. Every row is a marker (or a word on one) that the
package renders and prints; `docs/macros.md` is the full inventory and
`components.yaml` the catalog.

| I am writing… | Use |
|---|---|
| Rules or reference text under a heading | `@section panel` |
| Unboxed text that carries the accent rail | `@section flat` |
| A table or list to look up (prices, conditions, a menu of options) | `@section reference` |
| World or setting text | `@section lore` |
| Advice for the Dream Master, behind the screen | `@section dm` (a short one: `@callout dm`) |
| A choice the player writes on the Citizen File | `@section choose` |
| A term and its definition, or a glossary of terms | `@definition` |
| A boxed note, warning, DM note, vibe, origin or visit | `@callout …` (`@dm-note`) |
| A worked example | `@callout example` |
| A box in one of three registers: panel, slate, shard | `@block …` |
| Fiction, a chapter-opener story | `@fiction-excerpt` |
| A creature or NPC | `@npc-stat` (small ones: `@npc-stat compact`) |
| An organization: megacorp, cabal, cult, enforcers | `@faction megacorp`, `cabal`, `cult`, `enforcer` |
| General gear | `@gear` |
| A cybernetic or mod | `@gear augment` |
| A magic item or relic | `@gear treasure` |
| A vehicle | `@gear vehicle` |
| A drug, elixir or consumable | `@gear drug` |
| A labelled line in an entry: SPECS, Traits, Effects… | `**SPECS:**` (or `@field specs`; `specs` is the one SPECS box) |
| A titled run of entries, two columns | `@section catalog` with `@columns 2` |
| A roll-result ladder | a pipe table of the five bands (20, 11-19, 6-10, 2-5, 1), or `@outcome` |
| A random table with equal bands (1-4, 5-8, …) | `@roll-table` |
| Flaw, ideal or dream choices | `@flaws`, `@ideals`, `@dreams` (each a `choose` section holding a run of `@card`) |
| The Citizen File field list | `@citizen-walkthrough` |
| The specialty catalog | `@card-grid` |
| A specialty, its learning paths and skill cards | `@specialty`, `@learning-path`, `@skill` |
| Grouping, with no styling | `@section` |
| Where it sits | `@page chapter-start`, `intro`, `credits`, `contents`, `citizen-file` (and core's `blank`, `full-bleed`); `@chapter rules`, `lore`, `citizen-file`, `specialty` |

The named components are also words on `@section` (`@npc-stat` is
`@section npc`, `@fiction-excerpt` is `@section fiction`); either spelling
renders the same. `reference`, `lore`, `dm` and `choose` are words only: panels
that say what kind of text they hold. Write the content and the marker that says
what it is: the defaults set how it looks and where it breaks (sections split
across pages, a catalog too, and a creature and a callout stay whole). A page
or chapter word draws no box of its own: it re-tunes the sections inside it. To
change how one block sits, see [Author overrides](#author-overrides).

Also in the box:

- **More macros**, from `plugin.js`: `@specialty-intro` / `@specialty-art` /
  `@specialty-card`, `@continue` (a skill card that spans a page break),
  `@card`, `@procedure`, `@lede`, `@toc`, GFM alerts
  (`> [!NOTE]`, `[!WARNING]`, `[!DM]`, `[!VIBE]`, `[!ORIGIN]`, `[!VISIT]`,
  `[!FLAVOR]`, `[!PULLQUOTE]`), and the automatic `ROLL THE DIE!`
  chip. `docs/components-and-palette-reference.md` maps each to the classes it
  emits.
- **Seventeen stylesheets** under `styles/`, listed in `package.json` in
  cascade order: fonts and the layer statement, the palette and identity
  tokens, the element baseline, nine component sheets, page templates,
  paged-media rules, and `dc-native.css` — the engine-specific page chrome
  (brick-wall background, folios, chapter chips) that must stay last.
- **Fonts**: Titillium Web, Tomorrow and Lixdu, embedded into the PDF at
  build time.
- **Page and chapter words** every Dimm City book writes: `@page contents`,
  `credits`, `intro`, `chapter-start`, `citizen-file` (and `.dc-full-page`), and
  `@chapter rules`, `lore`, `citizen-file`, `specialty` for a chapter's section
  colour, plus the folio/chapter-chip chrome driven by `@chapter #id ch="N"`.
- **Snippets** for the app's snippet picker (`snippets/`): one per macro, per
  section, page and chapter word, and per modifier (`.dc-avoid-split`,
  `.dc-snug`), with placeholders for the parts you fill in.
- **`components.yaml`**: the catalog of every component — what you write,
  what lands in the HTML, which tokens are public, which sheet owns it.

## Quick start

Requires Gutterpress **0.11.0** or later — it wraps every extension's CSS in
its own cascade layer, so a book no longer needs a starter look removed
before this package can win the cascade.

```sh
gutterpress new "My Book" --preset dtrpg
gutterpress ext add gp-dimm-city my-book
gutterpress preview my-book
```

Then insert the *Toc Page*, *Credits Page* and *Chapter Start Page* snippets
to lay down the front matter, and reach for *Skill*, *Learning Path* and
*Specialty* as you write. `page-rules.css` sets a Letter page with bleed; keep
the manifest's `page:` in step with it.

## Author overrides

A book's markdown holds the content and the markers that say what it is
(`@section panel`, `@npc-stat`, `@gear augment`); the defaults above make it
look right and break sensibly. None of what follows is needed for that. These
are the supported ways to change one block when the defaults do not suit it:
written in the markdown, or from the book's own CSS, with the same effect. They
are documented and kept; the defaults only make them needed less often.

**Core Gutterpress classes (`gp-*`).** Image placement and size (`.gp-left`,
`.gp-right`, `.gp-center`, `.gp-full`, `.gp-bleed`, `.gp-small`, `.gp-medium`,
`.gp-large`), pinning art to the page (`.gp-pin` with `.gp-top`, `.gp-bottom`,
`.gp-flush`, `.gp-behind`), wrapping text around a shape (`.gp-shape`) and the
fragmentation helpers (`.gp-no-break`, `.gp-break-before`) belong to Gutterpress,
not to this package. They are written as `![alt](image.png){.gp-right
.gp-medium}` and are documented in the Gutterpress user guide
([Visual elements](https://github.com/dimm-city/gutterpress/blob/main/examples/gutterpress-user-guide/03-visual-elements.md)).
This package's defaults for art (below) read only an image with no class, so a
`gp-*` class always wins.

**Modifiers from this package.** Written after a marker (`@section panel
.dc-snug`) or in braces after an element (`## Title {.dc-h3}`). Each has a
matching setting for a book's CSS, so a book can do the same without a markdown
edit.

| Write | What it does | The same from a book's CSS |
|---|---|---|
| `.dc-avoid-split` on `@section`, `@skill`, `@faction` or `@npc-stat` | Keep that box on one page: it moves to the next page rather than splitting | `--dc-section-break-inside: avoid` with `--dc-section-edge: 0px` (a section), `--dc-skill-card-break-inside`, `--dc-faction-break-inside`, `--dc-npc-stat-break-inside` |
| `.dc-snug` on `@section` or `@page` | Tighten the space under paragraphs and list items, for one that overflows by a line or two | `--dc-flow-gap: 0.04in` |
| `.dc-h3` … `.dc-h6` on a heading or paragraph | Give it the look of that level without changing its place in the outline | none: a class only |
| `.dc-chevron` on a heading | Set it as a chevron banner (the title under `@page intro`, `credits` and `contents` already is one) | `--dc-chevron-bg`, `--dc-chevron-color`, `--dc-chevron-font-size` |
| `.dc-flush` | Run a tape, stat block, sticker chain, pull quote or `@outcome` edge to edge | none: a class only |
| `.dc-sidebar` on a callout | Float it right at about a third of the width, text wrapping on its left (`@callout note .dc-sidebar`) | none: a class only |
| `.dc-spray`, `.dc-spec-tweak`, `.dc-no-top`, `.dc-img-float-left`, `.dc-img-float-right` | Heading banners and an image float | none: classes only |

A catalog (`@section catalog`) splits across pages by default, since one kept
whole leaves the foot of the page before it blank; an explicit `.dc-avoid-split`
on it still keeps it whole, as does `--dc-catalog-break-inside: avoid` from a
book's CSS. An `@npc-stat` with at most one `####` is one creature and stays whole without
`.dc-avoid-split` (`--dc-npc-stat-break-inside: auto` lets one split). An image
with no class in a `@gear` entry floats right at half the card
(`--dc-entry-art-width`), and one on its own line under the credits colophon is
a band across the foot of the sheet (`--dc-credits-art-height`).

**Core markers and attributes.** `@page-break` starts a new page at that line;
`@columns 2` … `@end-columns` (one to five columns, and `@column-break` to move
to the next) is the one way to set text in columns. Both are Gutterpress's, not
this package's. `{#id}` (or `#id` on a marker line) names a block for a link and
for a book's CSS: `#core-loop { --dc-section-break-inside: avoid; }`. Written after
a table the package turns into an outcome ladder, or on an `@procedure` line, the
id and classes land on the ladder or the list.

**Coming: `[data-name]`.** Gutterpress will stamp a stable `data-name` on every
marker block, image and heading (from `name="…"`, then `label="…"`, then the
slug of its first heading, or the image's file name), so a book's CSS can tune
one block without touching the markdown:
`[data-name="core-loop"] { --dc-section-break-inside: avoid; }`. Until your
Gutterpress does, `name="…"` on a marker line writes it and `#id` works
everywhere.

## Your own CSS: the layer convention

List your sheets under `styles:` in the manifest. Gutterpress (0.11.0+) wraps
this whole package in its own cascade layer, `@layer ext.gp-dimm-city`, and
keeps the book's own `styles:` unlayered — so anything you write there beats
every rule in this package at any specificity, with no layer of your own to
declare:

```css
#chapter-03 { --dc-section-accent: var(--hud-magenta); }
```

The package's own sheets are layered internally (`@layer dc.tokens, dc.base,
dc.components, dc.templates, dc.pages`, nested inside `ext.gp-dimm-city`), and
`dc-native.css` stays last and unlayered within that internal stack — that's
a package-internal ordering concern, not something your book needs to work
around.

Never write bare `.dc-*` rules in a book to change a component; that fights
the package on every update. Reset the component's public tokens on a context
selector instead:

```css
.chapter-05 .dc-alert { --dc-alert-accent: var(--hud-blue); }
```

The tokens each component exposes are listed under `tokens:` in
`components.yaml`, and `styles/dc-component-defaults.css` is where their
defaults live.

## Versioning

Books pin an exact version, so nothing changes under you. To move a book to a
new release:

```sh
gutterpress ext add gp-dimm-city@1.5.0 my-book
```

Installing a version removes the book's copies of other versions of this
package, so there is nothing to clean up by hand. Commit the manifest change.

Rebuild and compare before you commit — the Dimm City books gate every bump
with a render-parity run (text runs, image placement, and a pixel comparison
of every page). Public API for semver purposes: the macro vocabulary, the
classes and tokens marked `live` in `components.yaml`, the page templates, and
the layer names. `CHANGELOG.md` lists what each release changes.

### Moving from 1.6.2 or earlier

1.6.3 changes a default, so rebuild and compare:

- An `@npc-stat` with at most one `####` (one creature) stays whole. Add
  `--dc-npc-stat-break-inside: auto` to let one split. A `.dc-avoid-split` on one
  is now redundant.

### Moving from 1.6.1 or earlier

1.6.2 folds the item markers into `@gear` and gives the SPECS box one spelling.
The old spellings are no longer recognised (a marker line prints as text, and
`@callout gear` reports an unknown variant), so rebuild after you migrate:

| Before | Now |
|---|---|
| `@augment` … `@end-augment` | `@gear augment` … `@end-gear` |
| `@treasure` … `@end-treasure` | `@gear treasure` … `@end-gear` |
| `@vehicle` … `@end-vehicle` | `@gear vehicle` … `@end-gear` |
| `@drug` … `@end-drug` | `@gear drug` … `@end-gear` |
| `@callout gear label="SPECS"` … `@end-callout` | `@field specs` … `@end-field` |
| `> [!GEAR]` | `@field specs` |

Any other `@callout gear label="…"` becomes `@field specs label="…"` for a
one-paragraph box, or `@callout note` for a longer note. A `**SPECS:**`
paragraph inside an entry needs no change.

## Licences

Code, stylesheets, catalog and docs: [MIT](LICENSE). Fonts carry their own
licences beside the files — `fonts/titillium-web/OFL.txt`,
`fonts/tomorrow/OFL.txt`, `fonts/lixdu/LICENSE.txt`. The Dimm City name, logo,
artwork and game text are not licensed by this package.

## Development

The short how-to is [docs/developing.md](./docs/developing.md): the edit → preview → test → release loop, in web-dev terms.

Everything you need to change the package and see the result is in this
repository: the plugin, the stylesheets, and `design-guide/` — the Dimm City
Design Guide, a Gutterpress book that documents every macro, token, component
and page template by rendering it. The guide's manifest loads the package from
this checkout (`extensions: - ../`), not from npm, so it is both the public
documentation and the test fixture: what it shows is what the working copy
renders.

```sh
bun install
npm run dev                  # live preview of the design guide, opens the browser
npm run build                # lint + validate + render .build/design-guide.pdf (needs Chrome 148+)
npm run build:html           # the guide as a static site, .build/design-guide-site/
bun test                     # plugin behaviour, design-guide render + snapshot, package, conventions
npm run test:update-snapshot # only when the plugin's output is meant to change
npm run pack:check           # what npm would publish
```

The loop is the usual web one. `npm run dev` runs `gutterpress preview
design-guide`: edit `plugin.js`, a sheet under `styles/`, a font or the brick
tile, or any chapter of the guide, and the preview re-renders (the CLI lists
each watched file as it starts). The Gutterpress desktop app does the same —
open the `design-guide/` folder in it. `npm run build` is the PDF the
reader gets; it runs Gutterpress's print-safety lint and source/PDF
validation and fails on an error. Set `CHROMIUM_PATH` if your Chrome is not
on a standard path.

The tests (`bun test`) are the CI gate:

- `test/design-guide.test.js` — every chapter renders through Gutterpress's
  pipeline with no layout warning and no marker left unrendered; every macro
  and alert type the plugin handles appears in the guide; each chapter's HTML
  matches `test/__snapshots__/`. A change to the plugin's output fails here
  until you run `npm run test:update-snapshot` and review the snapshot diff
  with the code.
- `test/plugin.test.js` — the loader contract and the behavioural edge cases.
- `test/package.test.js` — the tarball `npm publish` would ship: every
  declared path, every `url()` asset, one licence per font directory, the
  cascade contract.
- `test/conventions.test.js` — one prefix (`dc-`), no runtime imports, only
  allow-listed core hooks.

CI (`.github/workflows/ci.yml`) runs the tests and then builds the design
guide PDF with the PR's plugin and CSS, uploaded as the `design-guide-pdf`
artifact — open it to see what a change did to every page. On `main`, the
*Publish design guide* workflow deploys the HTML build to GitHub Pages
(enable it once under Settings → Pages → Source: GitHub Actions).

`plugin.js` imports nothing at runtime — `gutterpress` is a devDependency used
by the tests (`gutterpress/render`) and by the scripts (the CLI). Releases are
cut from the *Release* workflow (version in; npm, GitHub release and the
design guide PDF out); it refuses a version with no `## [X.Y.Z]` heading in
`CHANGELOG.md`. Issues about the package — a macro, a sheet, a token, a font,
or a page of the guide — belong here.
