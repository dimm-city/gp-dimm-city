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
  `@definition`, `@procedure`, `@lede`, `@toc`, `@tape`, `@glossary`, GFM
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

```sh
gutterpress new "My Book" --preset dtrpg
gutterpress ext add gp-dimm-city my-book
gutterpress preview my-book
```

Then, in the app, insert the *Toc Page*, *Credits Page* and *Chapter Start
Page* snippets to lay down the front matter, and reach for *Skill*,
*Learning Path* and *Specialty* as you write. `page-rules.css` sets a Letter
page with bleed; keep the manifest's `page:` in step with it.

## Your own CSS: the layer convention

List your sheets under `styles:` in the manifest. Extension styles always load
first, so yours come after. Wrap them in the `book` layer:

```css
@layer book {
  #chapter-03 { --dc-section-accent: var(--hud-magenta); }
}
```

The package declares `@layer dc.tokens, dc.base, dc.components, dc.templates,
dc.pages, book;` in its first sheet. `book` is last, so anything you put there
outranks every `dc.*` rule without a specificity contest. Two things to know:

- `dc-native.css` is deliberately **unlayered** so it beats every layered rule
  — a book that must override it lists an **unlayered** sheet after the
  extension; the last unlayered sheet wins.
- Do not invent layer names. A layer the package's statement does not name is
  created where it is first used, which puts it *after* `book` and silently
  above your own overrides.

Never write bare `.dc-*` rules in a book to change a component; that fights
the package on every update. Reset the component's public tokens on a context
selector instead:

```css
@layer book {
  .chapter-05 .dc-alert { --dc-alert-accent: var(--hud-blue); }
}
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

```sh
bun install
bun test                     # snapshot, behaviour, package and convention tests
bun run test:update-snapshot # only when the plugin's output is meant to change
bun run pack:check           # what npm would publish
```

`plugin.js` imports nothing at runtime — `gutterpress/render` is a
devDependency used only by the tests to run the plugin inside core's markdown
pipeline. Releases are cut from the *Release* workflow (version in, npm and
GitHub release out); it refuses a version with no `## [X.Y.Z]` heading in
`CHANGELOG.md`.

The design guide that documents this system in depth is a book in the
`dimm-city/dc-op-manual` repository. Issues about the package — a macro, a
sheet, a token, a font — belong here.
