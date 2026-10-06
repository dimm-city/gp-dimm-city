@chapter #ch-cli .cli .dg-guide ch="2"

# Publishing

@lede

Three commands cover the full authoring lifecycle: preview for live editing, build for output, validate for print compliance.

@end-lede

@page

## Essential Commands

| Command | What it does |
|---------|-------------|
| `gutterpress preview <project>` | Live preview server with hot reload — edits to markdown, CSS, or assets reflect immediately |
| `gutterpress build <project> --format pdf` | Render a PDF via Chromium |
| `gutterpress build <project> --format html` | Build a static HTML viewer for browser or deploy |
| `gutterpress build <project> --format pdfx` | Render a PDF/X-compliant PDF |
| `gutterpress validate <project> --pdf <file>` | Run source checks and validate a built PDF |

The full command set is `new`, `preview`, `build`, `publish`, `lint`, `validate`,
`audit`, `preflight`, `repair`. **There is no `run` subcommand.** An unrecognised
first positional is treated as an implicit `preview <that-name>`, so `gutterpress run …`
fails with `Input directory does not exist: ./run`. `build --format pdf|pdfx` already
lints and validates before and after rendering unless you pass `--skip-lint`,
`--skip-pre-validate`, or `--skip-post-validate`.

## Common Usage

```bash
# Live preview (from the gp-dimm-city repository root, `npm run dev` does the same)
gutterpress preview design-guide --open

# Build a print-ready PDF (`npm run build`)
gutterpress build design-guide --format pdf --out .build/design-guide.pdf

# Build a deployable HTML viewer (`npm run build:html`)
gutterpress build design-guide --format html --out .build/design-guide-site

# Print submission — PDF/X-1a with an ICC profile
gutterpress build design-guide --format pdfx --pdfx-flavor x1a \
  --icc /path/to/CGATS21_CRPC1.icc --out .build/design-guide.pdf
```

## Key Flags

| Flag | Commands | Purpose |
|------|----------|---------|
| `--port N` | preview | Port to listen on (default 3579) |
| `--format` | build | `html`, `pdf` (default), or `pdfx` |
| `--out` | build | Output directory, or a `.pdf` file path for `pdf`/`pdfx` |
| `--pdfx-flavor` | build | PDF/X flavor: `x1a` or `x3` — `--format pdfx` only |
| `--icc` | build | ICC profile path. **Optional** — falls back to manifest `pdfx.icc`, then to the profile embedded in Gutterpress |
| `--manifest` | build, validate | Path to `manifest.yaml` |
| `--category` | validate | `source`, `pdf`, `asset`, or `heuristic` |
