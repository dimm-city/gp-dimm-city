# Developing gp-dimm-city

The plugin, its stylesheets and the Dimm City Design Guide live in one repo,
and the guide loads the package from your working copy. So the loop is the
one you know from any front-end project: run a dev server, edit, watch the
page update, commit, open a PR.

## What's where

| Path | What it is |
|---|---|
| `plugin.js` | The markdown-it plugin: every `@macro` and `[!ALERT]` the system understands |
| `styles/` | The 16 stylesheets, listed in cascade order in `package.json` → `gutterpress.styles` |
| `snippets/` | What the desktop app's snippet picker inserts, one `.md` per macro |
| `components.yaml` | The component catalog: author syntax → emitted classes → public tokens → owning sheet |
| `fonts/`, `images/` | Assets the stylesheets reference with `url()` |
| `design-guide/` | The Design Guide book: documentation, live specimens, and the test fixture |

`design-guide/manifest.yaml` has `extensions: - ../`, so the guide renders
whatever is on disk in this checkout. No build step, no publish, no pin.

## Setup

```sh
bun install
```

That's it for previewing. Rendering a PDF needs Chrome or Chromium 148+ on a
standard path, or `CHROMIUM_PATH` pointing at one.

## The loop

**CLI:**

```sh
npm run dev
```

That runs `gutterpress preview design-guide --open`: the guide opens in your
browser and the server lists every file it watches. Edit any of them and the
page re-renders:

- `plugin.js` — change a macro, add one, fix emitted markup
- any sheet under `styles/` — tokens, components, page templates
- a font or image a sheet references
- any chapter under `design-guide/`

**Desktop app:** open the `design-guide/` folder as a book. Same preview, same
watching. The *Features* tab shows the package as a path extension.

Where to look while you work:

- `design-guide/05-text-and-callouts.md`, `06-panels-and-cards.md`,
  `07-specialty-system.md` — every component as a "you write / result"
  pair. Your component's live rendering, next to the markdown that makes it.
- `design-guide/10-reference.md` — every marker, class, and token on one page.
- `design-guide/03-palette.md` — every color token, swatched.

Two things the watcher does not do: it does not reload modules `plugin.js`
would import (it imports nothing, keep it that way), and it does not watch
`snippets/` or `components.yaml` (neither affects rendering).

## Changing a component's look

1. Find the sheet in `components.yaml` (`sheet:` under the component).
2. Edit the rule. Prefer resetting the component's public tokens
   (`--dc-*` in `styles/dc-component-defaults.css`) over new selectors.
3. Watch the gallery specimen update.

Rules worth knowing before you write CSS (the long form is
[css-architecture.md](./css-architecture.md)):

- Every class and custom property is `dc-` prefixed. `gp-` belongs to
  Gutterpress core; the stylesheets may *read* a short allow-list of core hooks
  (`.gp-columns-2`, `--gp-content-h`, …) and never declare one.
- Each sheet keeps all of its rules inside its own `@layer dc.<name> { … }`
  block, except `dc-native.css`, which is last and unlayered.
- A sheet must be listed in `package.json` → `gutterpress.styles` to load. No
  `@import`, no remote `url()`.
- `filter` and `clip-path` are print-risky; `npm run build` warns on each one.

## Adding a macro

The short path is [adding-macros.md](./adding-macros.md). The checklist:

1. `plugin.js` — the marker handler (copy the `@skill` shape).
2. `styles/components/<sheet>.css` — its rules, inside that sheet's layer.
3. `components.yaml` — the catalog entry.
4. `snippets/<name>.md` — with at least one `{{placeholder}}`.
5. The matching component chapter under `design-guide/` — a "you write /
   result" pair (a ```` ```markdown ```` fence with the source, then a
   `Result {.dg-result}` line, then the same markdown live). **Required**: a
   test fails if the plugin handles a macro the guide never demonstrates.
6. `design-guide/10-reference.md` — the one-line grammar entry.

Markers want a blank line on each side. `@end-procedure` directly under a
list item is folded into the item by markdown and never closes.

## Verify

```sh
bun test                      # ~90 tests, under 2 s
npm run test:update-snapshot  # when you MEANT to change rendered output
npm run build                 # lint + validate + .build/design-guide.pdf
npm run build:html            # the guide as a static site
```

`bun test` covers four things: the plugin's behaviour, the package npm would
publish, the conventions above, and the design guide itself. The guide test
renders every chapter through Gutterpress with your plugin, fails on any
layout warning or unrendered marker, and compares each chapter's HTML with
`test/__snapshots__/`. A change to what the plugin emits fails here until you
refresh the snapshot and review that diff alongside your code.

`npm run build` is what CI does on every PR, and the PDF it uploads as the
`design-guide-pdf` artifact is the whole-book view of your change.

## Ship

1. Branch, commit, open a PR to `main`. CI runs the tests and builds the PDF.
2. Add a line under `## [Unreleased]` in `CHANGELOG.md`. Public API for
   semver: the macro vocabulary, the classes and tokens marked `live` in
   `components.yaml`, the page templates, the layer names.
3. Merge. On `main`, the *Publish design guide* workflow deploys the HTML
   guide to GitHub Pages.
4. Release: Actions → *Release* → enter the version. It tests, bumps, tags,
   publishes to npm, and attaches the guide's PDF to the GitHub release.
   The workflow refuses a version with no `## [X.Y.Z]` changelog heading, so
   rename `[Unreleased]` first.
5. In a book: `gutterpress ext outdated` shows the new version,
   `gutterpress ext update gp-dimm-city` re-pins to it (Gutterpress 0.11.14+;
   `ext add gp-dimm-city@X.Y.Z` on older versions). Commit the manifest and
   `plugins/npm/` together.
