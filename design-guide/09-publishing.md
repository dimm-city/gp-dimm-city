@chapter #ch-publishing .cli .dg-guide ch="9"

@page .dg-doc

Chapter 9 {.dg-kicker}

# Publishing

Three commands cover the whole lifecycle: preview while you write, build for output, validate for print. The app and the CLI run the same engine. {.dg-lede}


## Commands

| Command | What it does |
|---|---|
| `gutterpress preview <book>` | Live preview with hot reload for markdown, CSS, and assets |
| `gutterpress build <book> --format pdf` | Render a PDF through Chromium's print engine |
| `gutterpress build <book> --format pdfx` | Render a PDF/X for a print service |
| `gutterpress build <book> --format html` | A static site of the book for the web |
| `gutterpress validate <book> --pdf <file>` | Source checks plus validation of a built PDF |
| `gutterpress lint <book>` | Print-safety lint over the book's stylesheets |

`build --format pdf` and `pdfx` lint and validate before and after rendering unless you pass `--skip-lint`, `--skip-pre-validate`, or `--skip-post-validate`.

```sh
# Preview a book
gutterpress preview my-book

# Print-ready PDF
gutterpress build my-book --format pdf --out ./dist/my-book.pdf

# Print submission: PDF/X-1a with an ICC profile
gutterpress build my-book --format pdfx --pdfx-flavor x1a --icc CGATS21_CRPC1.icc --out ./dist/my-book.pdf

# Static site
gutterpress build my-book --format html --out ./dist/site
```

## DriveThruRPG

The package's page geometry follows DriveThruRPG's print specification: 0.125 in bleed on the three outside edges, all text 0.5 in inside the trim ([Page Templates](#ch-templates)). With gutterpress 0.11.15 or later, `preset: dtrpg` covers the rest:

| Setting (preset default) | What it does |
|---|---|
| `print: { signature: 4, reserveLastPage: true }` | Pads the interior to DriveThruRPG's 4-page signature and always ends on a completely blank page — the page reserved for printer information. The build log's page count is the number to enter in the cover Template Generator. |
| `pdfx.blackText: k-only` | In a `--format pdfx` build, near-black text (the book's ink included) prints on the black plate only, as DriveThruRPG asks for text at 24 pt and below. Black rules and panels keep their rich black, which the ICC conversion makes heavy: see the ink tokens in [Color](#ch-palette). |

Don't set `print.signature` yourself, and don't end the book with a blank page of your own: the preset does both. (`@page .dc-printer-page`, the package's stand-in from before gutterpress 0.11.15, was removed in 1.1.2.)

## Art must be opaque

PDF/X-1a and X-3 have no transparency. When an image carries an alpha channel (an RGBA PNG, or a PNG with a transparent palette entry), Ghostscript flattens **every page that shows it** into one full-page bitmap: the page's live text, rules and vector chrome become pixels, the fonts drop out and the text is no longer sharp or searchable. The build only warns (`Image contains alpha channel`).

Flatten each image onto the solid colour it will sit on, at full resolution, before it goes into the book: an image on a cream panel flattens onto `--paper-cream` (`#f0eee9`), one on a dark card onto that card's dark. Export with no alpha channel, or with ImageMagick:

```sh
convert art.png -background '#f0eee9' -alpha remove -alpha off PNG24:art.png
```

Use a PNG of colour type 2 (RGB) or a JPEG; never a PNG with transparency, GIF, WebP or an SVG with `opacity`. The package's own test (`test/images.test.js`) fails on any alpha channel under `design-guide/img/`, and on a remote image URL in the guide: a placeholder service fails offline. `scripts/make-placeholders.mjs` regenerates the guide's placeholder art with ImageMagick.

## Flags

| Flag | Commands | Purpose |
|---|---|---|
| `--port N` | preview | Port to listen on (default 3579) |
| `--open` | preview | Open the browser |
| `--format` | build | `html`, `pdf` (default), or `pdfx` |
| `--out` | build | Output directory, or a `.pdf` path for `pdf` / `pdfx` |
| `--pdfx-flavor` | build | `x1a` or `x3`, with `--format pdfx` |
| `--icc` | build | ICC profile; falls back to the manifest's `pdfx.icc`, then the embedded profile |
| `--category` | validate | `source`, `pdf`, `asset`, or `heuristic` |

## Keeping the package current

A book pins an exact package version and builds from the copy vendored under `plugins/npm/`. To see whether a newer version exists and move to it:

```sh
gutterpress ext outdated my-book            # each pinned package against npm's latest
gutterpress ext update gp-dimm-city my-book # re-pin to the latest; the old copy is removed
```

Commit the manifest; `plugins/npm/` is in the book's `.gitignore`, and a fresh clone downloads the pinned version on its first build or `gutterpress validate`. The Gutterpress app does the same under Project settings → Features.

## This guide

From the package repository, `npm run dev` previews this guide against the working copy, `npm run build` renders it to `.build/design-guide.pdf`, and `npm run build:html` builds the static site. The developer workflow is in the repository's `docs/developing.md`.
