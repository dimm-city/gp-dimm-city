@chapter #ch-publishing .cli .dg-guide ch="9"

@page

# Publishing

@lede

Three commands cover the whole lifecycle: preview while you write, build for output, validate for print. The app and the CLI run the same engine.

@end-lede


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

Commit the manifest and `plugins/npm/` together. The Gutterpress app does the same under Project settings → Features.

## This guide

From the package repository, `npm run dev` previews this guide against the working copy, `npm run build` renders it to `.build/design-guide.pdf`, and `npm run build:html` builds the static site. The developer workflow is in the repository's `docs/developing.md`.
