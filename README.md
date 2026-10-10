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
  - gp-dimm-city@1.0.0
```

**Commit `plugins/npm/`.** Builds never fetch from the registry; the vendored
copy is what builds your book, on every machine and in CI. If your repo
ignores `node_modules`, add `!**/plugins/npm/**` as the last line of
`.gitignore` — the vendored tree has a `node_modules` folder inside it — and
`**/plugins/npm/** -text` to `.gitattributes`, because the copy is verified
byte for byte on every build.

`gutterpress ext list my-book` shows `gp-dimm-city@1.0.0 [npm; markdown, styles, components, snippets]`.

## What you get

- **Macros**, from `plugin.js`: `@specialty` / `@specialty-intro` /
  `@specialty-art` / `@specialty-card`, `@learning-path`, `@skill` (with
  `@continue` for a card that spans a page break), `@outcome`, `@callout`,
  `@dm-note`, `@sidebar`, `@sidebar-box`, `@block`, `@card`, `@gear`,
  `@definition`, `@procedure`, `@lede`, `@toc`, `@glossary`, GFM
  alerts (`> [!NOTE]`, `[!WARNING]`, `[!DM]`, `[!VIBE]`, `[!ORIGIN]`,
  `[!VISIT]`, `[!GEAR]`, `[!FLAVOR]`, `[!PULLQUOTE]`), and the automatic
  `ROLL THE DIE!` chip. `docs/macros.md` is the inventory;
  `docs/components-and-palette-reference.md` maps each to the classes it
  emits.
- **Sixteen stylesheets** under `styles/`, listed in `package.json` in
  cascade order: fonts and the layer statement, the palette and identity
  tokens, the element baseline, eight component sheets, page templates,
  paged-media rules, and `dc-native.css` — the engine-specific page chrome
  (brick-wall background, folios, chapter chips) that must stay last.
- **Fonts**: Titillium Web, Tomorrow and Lixdu, embedded into the PDF at
  build time.
- **Page templates** every Dimm City book writes: `.page-toc`,
  `.page-credits .dc-credits`, `.page-chapter-start .dc-chapter-start`,
  `.dc-full-page`, plus the folio/chapter-chip chrome driven by
  `@chapter #id ch="N"`.
- **Snippets** for the app's snippet picker (`snippets/`): one per macro and
  one per front-matter page, with placeholders for the parts you fill in.
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
gutterpress ext add gp-dimm-city@1.1.0 my-book
git rm -r my-book/plugins/npm/gp-dimm-city/1.0.0   # ext add leaves the old copy in place
```

Rebuild and compare before you commit — the Dimm City books gate every bump
with a render-parity run (text runs, image placement, and a pixel comparison
of every page). Public API for semver purposes: the macro vocabulary, the
classes and tokens marked `live` in `components.yaml`, the page templates, and
the layer names. `CHANGELOG.md` lists what each release changes.

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
