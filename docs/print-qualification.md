# Print qualification: preserve-text PDF/X

What this package prints in a DriveThruRPG PDF/X-1a build with Gutterpress's
`pdfx.transparency: preserve-text`, measured, component by component (#43).
The design guide is the specimen book: it shows every default component and
opts into `preserve-text` in its manifest.

## Setup

| | |
|---|---|
| Package | gp-dimm-city 1.8.0 (`release/1.8.0`, after 1.8.0-alpha.2) |
| Renderer | Gutterpress 0.11.20-alpha.4, `--format pdfx`, preset `dtrpg` (its default ICC profile) |
| Browser | Chromium 141.0.7390.37 |
| Ghostscript | 10.02.1 |
| Fonts | the package's own (`fonts/`: Lixdu, Tomorrow, Titillium Web) |

Each source was built twice, as `--format pdf` and as `--format pdfx`, and the
two files were compared page by page.

## Results

**Design guide, 144 pages.**

- **No fallbacks.** 75 pages use transparency and were split: their artwork
  is rasterised at 300 DPI and their text drawn live on top. The other 69
  pages hold no transparency and stay fully vector. No page fell back to
  whole-page flattening.
- **Fonts.** Every page with text embeds its fonts (101 CID TrueType
  subsets), with no Type 3.
- **Text.** Each page's text extracts the same as from the plain PDF. The
  only differences are invisible word joiners (U+2060) and line-end hyphens,
  which the two files report differently.
- **Black text.** On every page sampled (4, 13, 50, 70, 111, 125, 136,
  vector and split), no pixel at 90% black or more carries cyan, magenta or
  yellow.
- **Appearance.** Every page matches the plain PDF apart from CMYK gamut
  shifts: saturated colours such as the lime outcome chip and the cyan tab
  print duller. That is the conversion to print colour, not the split.

**Field Guide (dc-op-manual), 192 pages, on 1.8.0-alpha.2.** 183 pages
split, 9 text-free pages (art plates) flattened whole, and no fallbacks.
Every text page embeds its fonts, with no Type 3, and its body text is
black ink only.

## Components

"Split" means the specimen page uses transparency and printed split, with
live text. "Vector" means the page has no transparency and printed as vector
PDF. Every row matched the plain PDF at 300 DPI, apart from CMYK gamut.

| Component | Specimen pages (design guide) | Printed | Notes |
|---|---|---|---|
| Brick wall (`@page` background) | every wall page | split and vector | opaque tile, 900px across a 1.5in repeat (600 DPI) |
| Section panels, soft lift, hard shadow | 21, 23, 24, 125–140 | split | |
| Recessed `lore` / `dm` / `choose` | 33, 131 | split | soft inset |
| Fiction excerpt | 33, 83 | split, vector | |
| Skill cards: tab gloss, tape, AP chips | 62, 84, 89 | vector, split | |
| Outcome ladder | 38, 39, 65, 66, 98, 122, 129, 138 | split | key gloss kept |
| Path banners, specialty cards | 94, 116, 117 | split | |
| Tape divider (normal, `dc-flush`) | 28, 82, 99, and a fixture | vector, split | tiled stripes regular in both |
| Stickers, pull quotes | 24, 62, 69, 82, 85 | split, vector | |
| Spray mark | 11, 81, 100, 131 | vector, split | |
| Rules and dividers | 38, 69, 105 | split, vector | hairlines and dotted rules intact |
| Credits | 71, 81, 108 | vector, split | |
| Factions (incl. hazard stripe) | 30, 47, 83, 102, 136 | split, vector | |
| Stat blocks, NPCs, tables | 50–54, 132–135 | split, vector | |
| Callouts | 15, 18, 21, 23–29 | vector, split | |
| Gear entries | 42, 45, 105, 106, 139, 140 | vector, split | |

Crops at 300 DPI (PDF left, PDF/X right):

- [Outcome ladder and a faction card](print-qualification/outcome-and-faction.jpg)
- [A numbered list with its soft lift, and a `choose` panel](print-qualification/list-and-choose.jpg)
- [The brick wall and a paper slip](print-qualification/wall-and-slip.jpg)
- [Tape, normal and `dc-flush`, between body text (150 DPI)](print-qualification/tape.jpg)

## What preserve-text does not cover

These limits belong to the renderer, and upgrading this package does not
lift them. The package's own styles stay inside them, and its tests enforce
the first three.

- **Text must be opaque.** A page whose text is drawn with transparency
  (opacity, `mix-blend-mode`, a soft mask, a translucent `text-shadow`)
  cannot keep its text live: it is flattened whole. The control run shows
  this. Setting `--dc-outcome-name-opacity: 0.6` on one page flattened that
  page, with no fonts, and the build named the cause ("text drawn with
  transparency or blending"). The page next to it, at the default `1`, split
  with live text. Test: *keep text opaque*.
- **No `filter` on an element that holds text.** Chromium prints a filtered
  element's text as a picture, in the plain PDF as well. A filter may sit
  only on a text-free `::before`/`::after` layer. Test: *put a filter only on
  a ::before or ::after layer*.
- **No repeating gradients.** PDF/X drops them. Tile an ordinary gradient
  instead. Test: *use no repeating gradient*.
- **Text prints above all artwork.** On a split page, text is redrawn on top
  of the flattened artwork. A decoration painted over text in the browser
  (a tint or a mark above a glyph) loses its effect in print. No default
  component overlaps text. The skill card's tape sits on the card edge, clear
  of the first line (checked with a full-width first line, #42).
- **Artwork is a 300 DPI picture.** On a split page, rules, fills and shapes
  are raster, including ones that are vector in the plain PDF. 300 DPI is
  DriveThruRPG's colour requirement. `pdfx.rasterDpi` raises it, at a cost in
  file size: the Field Guide's PDF/X is about 366 MB at 300 DPI, since
  Gutterpress keeps those images lossless.
- **A page can be flattened whole on purpose.** `pdfx.flattenPages` lists
  pages to flatten whole, keeping a composition that must paint above its
  text at the cost of that page's live text. List pages by physical page
  number, and re-check the list after the book reflows.

## Re-running it

```sh
gutterpress build design-guide --format pdf  --out .build/dg.pdf
gutterpress build design-guide --format pdfx --out .build/dg-x.pdf
```

The build reports the split pages, any page that falls back and why, and
any text-free page it flattens whole. Then check `pdffonts` (fonts embedded,
no Type 3), `pdftotext` against the plain PDF, and the separations
(`gs -sDEVICE=tiffsep`) for black text on the black plate only.
