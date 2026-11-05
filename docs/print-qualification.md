# Print qualification: preserve-text PDF/X

What this package prints in a DriveThruRPG PDF/X-1a build with Gutterpress's
`pdfx.transparency: preserve-text`, measured, component by component (#43).
The design guide is the specimen book: it shows every default component and
opts into `preserve-text` in its manifest.

## Setup

| | |
|---|---|
| Package | gp-dimm-city 1.10.2-alpha.2 (`release/1.10.2`, with the 300 DPI art and ground) |
| Renderer | Gutterpress 0.11.24-alpha.1, `--format pdf` and `--format pdfx`, preset `dtrpg` (CGATS21_CRPC1), `pdfx.transparency: preserve-text` from the guide's manifest |
| Browser | Chrome for Testing 153.0.8010.12 (Skia/PDF m153) |
| Ghostscript | 10.05.0 (honours the output profile; 10.02.1, which the 1.8.0 run used, separated through its default profile) |
| Fonts | the package's own (`fonts/`: Lixdu, Tomorrow, Titillium Web) and the guide's code face (IBM Plex Mono) |

The guide was built twice, as `--format pdf` and as `--format pdfx`, and the
two files were compared page by page. The renderer was the 0.11.24-alpha.1
source checkout (`bun packages/cli/src/cli.ts`), not the package installed in
`node_modules`: that copy, the same version, could not inspect the rendered
PDF's text on this machine ("doc.destroy is not a function") and flattened
every page that uses transparency whole, as `flatten-page` would. The source
checkout split them.

## Results

**Design guide, 176 pages** (621 × 810 pt, PDF 1.3 / X-1a; 75.5 MB against
the plain PDF's 11.4 MB).

- **No fallbacks.** 78 pages use transparency and were split: their artwork
  is rasterised at 300 DPI and their text drawn live on top. The other 98
  pages hold no transparency and stay fully vector, the three text-free
  plates (73, 143, 149) and the three closing blanks among them. No page fell
  back to whole-page flattening.
- **Fonts.** Every page with text embeds its fonts (23 CID TrueType subsets),
  with no Type 3; the build's `pdf.print.embedded-fonts` check reports
  nothing.
- **Output intent.** One `/OutputConditionIdentifier (CGATS21-2-CRPC1)`
  (`qpdf --qdf --object-streams=disable dg-x.pdf - | grep -a
  OutputConditionIdentifier`).
- **Text.** Each page's text extracts the same as from the plain PDF, once
  the word joiners (U+2060) and line-end hyphens the two files report
  differently are set aside; the one remaining difference is a space
  `pdftotext` puts inside one word on page 60 in one file and not the other.
- **Black text.** The build's `pdf.print.black-text` check, which reads every
  run of dark four-colour text at 24pt or under, finds none (0 runs): `#000`
  and `--ink` text prints on the black plate alone. (A pixel test at 90% K no
  longer says anything: `--ink` fills, chips and tabs separate to C44 M38 Y37
  K92 through CRPC1, as the token comments record.)
- **Ink.** The ink-coverage check reports only pages over 240% and reports
  none. Measured the way it measures (72 DPI CMYK raster, each page's
  heaviest spot), the heaviest page is 131 (the image floats in the Variant
  Gallery) at C50.6 M42.7 Y35.3 K92.9 = 221.6%, then 26 (221.2%) and 137
  (220.8%); a plain `--ink` page is 212.2%.
- **Resolution.** No image prints under 300 DPI: the pre-render check and
  the post-build `pdf.print.image-resolution` check are both silent (on
  1.10.2-alpha.2 they named 14 images and four pages).
- **Appearance.** Every page matches the plain PDF apart from CMYK gamut
  shifts: saturated colours such as the lime outcome chip and the cyan tab
  print duller. That is the conversion to print colour, not the split.
- **Remaining warnings.** One: the list of the 78 split pages, which
  preserve-text prints by design. The post-build report adds four
  informational lines (low text density on pages 12, 55, 96 and 132; no
  internal link annotations; no explicit page labels), none a print fault.

**Field Guide (dc-op-manual), 192 pages, on 1.8.0-alpha.2** (not re-run for
1.10.2; the book is outside this repository). 183 pages split, 9 text-free
pages (art plates) flattened whole, and no fallbacks. Every text page embeds
its fonts, with no Type 3, and its body text is black ink only.

## Components

"Split" means the specimen page uses transparency and printed split, with
live text. "Vector" means the page has no transparency and printed as vector
PDF. Every row matched the plain PDF at 300 DPI, apart from CMYK gamut.

| Component | Specimen pages (design guide) | Printed | Notes |
|---|---|---|---|
| Brick wall (`@page` background) | every wall page | split and vector | opaque tile, 900px across a 1.5in repeat (600 DPI); the ground strip 300 DPI; the six stone walls about 240 DPI, accepted as texture |
| Section panels, soft lift, hard shadow | 39, 68, 69, 155, 163 | split | |
| Recessed `lore` / `dm` / `choose` | 42, 163 | split | soft inset |
| Fiction excerpt | 43, 91, 139, 142 | vector | the broken-wall edge is clipped vector shapes |
| Skill cards: tab, bolt, AP chips | 76–83, 109–115, 150–153 | vector, split | the tab gloss is pre-mixed (1.10.2) |
| Outcome ladder | 50, 124, 161 | split | key bevel kept |
| Path banners, specialty cards | 72, 74, 75, 77–81, 118, 119, 144–147 | vector, split | |
| Tape divider (normal, `dc-flush`) | 36, 126, 165 | split, vector | tiled stripes regular in both |
| Stickers, pull quotes | 30, 75, 77–81, 137 | split | |
| Spray mark | 16, 127 | split | |
| Rules and dividers | 36, 165 | split | hairlines (1pt, `--ink`) and dotted rules intact |
| Credits | 136 | split | |
| Factions (incl. hazard stripe) | 61, 62, 169 | vector, split | |
| Stat blocks, NPCs, tables | 42, 63–68, 164–167 | split, vector | |
| Callouts | 29–35, 159 | split, vector | |
| Gear entries | 53–60, 170–173 | vector, split | |

Crops at 300 DPI (PDF left, PDF/X right), from this build (the 1.8.0 set
showed cream paper, 0.75pt hairlines and the layered gloss, all changed since):

- [Outcome ladder (p. 50) and a faction card (p. 62)](print-qualification/outcome-and-faction.jpg)
- [A numbered list with its soft lift (p. 155), and a `choose` panel (p. 42)](print-qualification/list-and-choose.jpg)
- [The brick wall and a paper slip (p. 163)](print-qualification/wall-and-slip.jpg)
- [Tape, normal and `dc-flush` (p. 126, 150 DPI)](print-qualification/tape.jpg)

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
  component overlaps text. The skill card's bolt sits in the corner, clear
  of the first line (checked with a full-width first line, #42).
- **Artwork is a 300 DPI picture.** On a split page, rules, fills and shapes
  are raster, including ones that are vector in the plain PDF. 300 DPI is
  DriveThruRPG's colour requirement. `pdfx.rasterDpi` raises it, at a cost in
  file size: the Field Guide's PDF/X was about 366 MB at 300 DPI on 1.8.0,
  and the design guide's is 75.5 MB, since Gutterpress keeps those images
  lossless.
- **A page can be flattened whole on purpose.** `pdfx.flattenPages` lists
  pages to flatten whole, keeping a composition that must paint above its
  text at the cost of that page's live text. List pages by physical page
  number, and re-check the list after the book reflows.

## Re-running it

```sh
gutterpress build design-guide --format pdf  --out .build/dg.pdf
gutterpress build design-guide --format pdfx --out .build/dg-x.pdf
```

If the build says it "could not inspect this PDF's text" and flattened every
transparent page whole, run the same commands from a Gutterpress source
checkout (`bun packages/cli/src/cli.ts build …`), as this run did.

The build reports the split pages, any page that falls back and why, and
any text-free page it flattens whole; its post-build checks report only
faults, so a silent `pdf.print.embedded-fonts`, `pdf.print.black-text`,
`pdf.print.ink-coverage` and `pdf.print.image-resolution` is a pass. Then
check `pdffonts` (fonts embedded, no Type 3), `pdftotext` against the plain
PDF, and the output intent with `qpdf --qdf --object-streams=disable
dg-x.pdf - | grep -a OutputConditionIdentifier`.
