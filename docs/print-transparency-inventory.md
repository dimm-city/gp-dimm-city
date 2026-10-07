# Print transparency inventory

**Why this exists.** PDF/X-1a, the format DriveThruRPG accepts for print, has no transparency. Ghostscript flattens any page that uses it into a single raster image. That page loses its live text and embedded fonts, and gutterpress's `pdfx.blackText: k-only` rewrite (black text on the black plate only) can't reach its text. This package used transparency in 26 places: an RGBA brick tile with a blend mode, semi-transparent shadows, tinted fills and `opacity`. On the Field Guide, **185 of 232 pages** came out image-only.

Every one of those uses is now opaque. Each colour is **pre-composited** with `color-mix()`: it is the colour the transparency produced on the surface it sits on. The brick wall is an opaque tile baked the same way. This document lists every change, so the books can be checked visually against it.

A test enforces it: `test/conventions.test.js` → *paint nothing transparent (PDF/X-1a)* fails on any `rgba()`/`hsla()`, `opacity` below 1, 8-digit hex, blend mode, transparent gradient stop or blurred shadow in the package's stylesheets.

## How to verify a book

1. Build the book (`--format pdf`) before and after the change and compare the pages listed under *Where it changed* below. Each entry under *Changes* says what to look at.
2. Expect shadows and tints to keep their colour. The difference is that a shadow on the brick wall is now a **flat tone** where it used to show the wall texture darkened. Check that it still reads as a shadow, not a grey band.
3. Build `--format pdfx` and confirm pages keep live text: `pdftotext -f N -l N book.pdf -` prints the page's words. A page that prints nothing has been flattened.

## The wall

| | Before | After |
|---|---|---|
| Image | `images/brick-bg-01.png`, RGBA, 3.8 MB | `images/brick-wall.png`, RGB, 2.2 MB: the RGBA tile multiplied into `--bg` (`#c8c5bf`) and flattened |
| Rule | `background: var(--bg) url(brick-bg-01.png); background-blend-mode: multiply` | `background: var(--bg) url(brick-wall.png)`, no blend mode (`dc-native.css` §1; the guide's `.dg-stage`) |
| Look | | Same: design-guide wall pages differ by 0.15/255 on average |
| Note | | A book that changes `--bg` no longer tints the brick. The RGBA source is in `source-art/` (unpublished), with the bake recipe in `dc-native.css` |

`--wall-tone: #c1beb8` is the opaque tile's average colour. Shadows that land on the wall mix against it.

## Changes

| ID | Component | Before | After | Mixed against | What to look at |
|---|---|---|---|---|---|
| T1 | Poster shadow token `--shadow-poster` (`dc-palette.css`) | `rgba(0, 0, 0, 0.28)` | `color-mix(in srgb, #000 28%, var(--wall-tone))` | the brick wall | Every lede (chapter openers, How Abilities Work), the Contents and Credits panels, specialty cards, the Introduction section, stat grids. The shadow is now a flat tone instead of a darkened view of the brick: check it reads as a shadow, not a grey band. |
| T2 | Chapter-opener shadow token `--dc-chapter-opener-shadow` (`dc-palette.css`) | `--dc-chapter-opener-shadow: 3px 4px 0 rgba(0, 0, 0, 0.28);` | `--dc-chapter-opener-shadow: 3px 4px 0 color-mix(in srgb, #000 28%, var(--wall-tone));` | the brick wall | Labelled chapter openers (design guide Part 2: C.01, C.02, C.1): the badge's drop shadow. |
| T3 | `--dc-pullquote-accent-soft` (pull-quote right rule) (`dc-component-defaults.css`) | `rgba(230, 0, 122, 0.15)` | `color-mix(in srgb, rgb(230 0 122) 15%, var(--dc-pullquote-bg))` | the pull-quote panel (`--dc-pullquote-bg`) | Pull quotes: the thin right rule (design guide ch.5 Pull quote; Field Guide pull quotes). |
| T4 | `--dc-sidebar-callout-bg` (inset-rail callout paragraph) (`dc-component-defaults.css`) | `rgba(42, 106, 138, 0.08)` | `color-mix(in srgb, rgb(42 106 138) 8%, var(--dc-sidebar-surface))` | the sidebar surface | Inset sidebar rail paragraphs after an `---` (design guide ch.4 inset sidebar page if used). |
| T5 | `--dc-tape-border` (tape divider border) (`dc-component-defaults.css`) | `rgba(212, 18, 0, 0.60)` | `color-mix(in srgb, rgb(212 18 0) 60%, var(--dc-tape-bg))` | the tape fill (`--dc-tape-bg`) | Tape dividers (design guide ch.5 Tape, Variant Gallery Tape; Field Guide NPC tiers). |
| T6 | `--dc-outcome-name-opacity` default (outcome-ladder result names) (`dc-component-defaults.css`) | `--dc-outcome-name-opacity: 0.85;` | `--dc-outcome-name-opacity: 1;` | — | See O2: the 85% is now mixed into the colour instead. |
| C1 | Blockquote right rule (`dc-core.css`) | `border-right: 2px solid rgba(230, 0, 122, 0.18);` | `border-right: 2px solid color-mix(in srgb, rgb(230 0 122) 18%, var(--paper-stain));` | the blockquote fill (`--paper-stain`) | Plain `>` quotes and epigraphs: the thin magenta right rule. |
| C2 | Spray banner smudge (`.dc-spray::after`) (`components/chrome.css`) | `background: var(--dc-spray-bg); opacity: 0.08; }` | `background: color-mix(in srgb, var(--dc-spray-bg) 8%, var(--wall-tone)); }` | the brick wall | Standalone spray headings (`## … {.dc-spray}`): the faint bar under the banner. |
| C3 | Path sticker shadow (`.dc-sticker`) (`components/chrome.css`) | `box-shadow: 2px 2px 0 rgba(0, 0, 0, 0.35);` | `box-shadow: 2px 2px 0 color-mix(in srgb, #000 35%, var(--paper-cream));` | the path panel (paper cream) | Learning-path skill stickers (every skill tree): the small drop shadow. |
| C4 | Active path sticker shadow (`.dc-sticker.active`) (`components/chrome.css`) | `box-shadow: 2px 2px 0 rgba(0, 0, 0, 0.28);` | `box-shadow: 2px 2px 0 color-mix(in srgb, #000 28%, var(--paper-cream));` | the path panel (paper cream) | The highlighted sticker in a path row. |
| C5 | Path title sticker shadow (`.dc-path-sticker`) (`components/chrome.css`) | `box-shadow: 1px 2px 0 rgba(0, 0, 0, 0.30);` | `box-shadow: 1px 2px 0 color-mix(in srgb, #000 30%, var(--dc-path-title-bg));` | the path title bar | The tier tag (e.g. AUG1) in each path banner. |
| C6 | Sticker tier reference text (`.dc-sticker-ref`) (`components/chrome.css`) | `color: inherit; opacity: 0.55;` | `color: color-mix(in srgb, currentColor 55%, var(--ink-dark));` | the sticker fill (`--ink-dark`) | The small number before each sticker name in path rows (e.g. "1" in "1 · PUNISHING COUNTER"). |
| C7 | Dashed rule (`hr`, `.dc-dashed-rule`) (`components/chrome.css`) | `border-top: 1.5px dashed var(--hud-magenta); opacity: 0.5;` | `border-top: 1.5px dashed color-mix(in srgb, var(--hud-magenta) 50%, var(--paper-cream));` | a paper panel (paper cream) | Every `---` rule: gear lists, sidebar boxes, NPC entries (design guide ch.5 Dashed rule; Field Guide gear chapter). |
| C8 | Tape shadow (`.dc-tape`) (`components/chrome.css`) | `box-shadow: 1px 1px 0 rgba(0, 0, 0, 0.15);` | `box-shadow: 1px 1px 0 color-mix(in srgb, #000 15%, var(--wall-tone));` | the brick wall | Tape dividers: the 1px shadow. |
| C9 | Tape dash pattern (`.dc-tape::after`) (`components/chrome.css`) | `background: repeating-linear-gradient(90deg, var(--crimson) 0 6px, transparent 6px 10px); opacity: 0.85;` | `background: repeating-linear-gradient(90deg, color-mix(in srgb, var(--crimson) 85%, var(--dc-tape-bg)) 0 6px, var(--dc-tape-bg) 6px 10px);` | the tape fill | Tape dividers: the dashed crimson rule after the label. |
| K1 | Skill-card body shadow (`.dc-card-inner::before`) (`components/cards.css`) | `background: rgba(0, 0, 0, 0.28); clip-path: var(--dc-skill-body-shape);` | `background: color-mix(in srgb, #000 28%, var(--wall-tone)); clip-path: var(--dc-skill-body-shape);` | the brick wall | Every skill card: the offset shadow behind the body (all ten skill trees; Field Guide specialty chapters). |
| K2 | Skill-card corner mark (`.dc-card-body::before`) (`components/cards.css`) | `background: var(--dc-card-body-mark); opacity: 0.15;` | `background: color-mix(in srgb, var(--dc-card-body-mark) 15%, var(--dc-card-surface));` | the card surface | The faint tilted dash at a skill card body's top right. |
| K3 | Highlight card glow (`.dc-highlight-body`) (`components/cards.css`) | `linear-gradient(to bottom, rgba(180, 40, 40, 0.10) 0%, rgba(180, 40, 40, 0) 45%),` | `linear-gradient(to bottom, color-mix(in srgb, rgb(180 40 40) 10%, var(--dc-card-surface)) 0%, var(--dc-card-surface) 45%),` | the card surface | Highlighted skill cards (`\| highlight`, `{.dc-highlight}`): the faint red wash at the top. |
| K4 | AP chip bevel and shadows (`.dc-ap`) (`components/cards.css`) | `inset 0 1px 0 rgba(255, 255, 255, 0.15), 2px 2px 0 rgba(0, 0, 0, 0.10), 3px 3px 6px rgba(0, 0, 0, 0.08); text-shadow: 0 1px 0 rgba(0, 0, 0, 0.20);` | `inset 0 1px 0 color-mix(in srgb, #fff 15%, var(--dc-ap-bg)), 2px 2px 0 color-mix(in srgb, #000 10%, var(--dc-card-surface)); text-shadow: 0 1px 0 colo…` | the chip fill (bevel, text shadow) and the card surface (drop shadow) | Every AP chip: the top bevel line, the hard 2px shadow, the text shadow. The soft 6px blurred shadow is REMOVED (a blur is transparency by nature). |
| O1 | Outcome key bevel (`.dc-outcome-key`) (`components/data.css`) | `inset 0 1px 0 rgba(255, 255, 255, 0.12), inset 0 -1px 0 rgba(0, 0, 0, 0.18);` | `inset 0 1px 0 color-mix(in srgb, #fff 12%, var(--row-color, var(--ink))), inset 0 -1px 0 color-mix(in srgb, #000 18%, var(--row-color, var(--ink)));` | the key's own fill | Outcome ladders (Variant Gallery Outcome ladder; skill cards with outcome tables): the 1px light top and dark bottom lines on each roll key. |
| O2 | Outcome result name (`.dc-outcome-key .dc-outcome-name`) (`components/data.css`) | `color: var(--dc-outcome-name-color); opacity: var(--dc-outcome-name-opacity);` | `color: color-mix(in srgb, var(--dc-outcome-name-color) 85%, var(--row-color, var(--ink))); opacity: var(--dc-outcome-name-opacity);` | the key's own fill | Outcome ladders: the small result word under each roll (TRIUMPH, SUCCESS…). |
| O3 | Pull-quote mark (`.dc-pullquote::before`) (`components/data.css`) | `color: var(--hud-magenta); opacity: 0.55;` | `color: color-mix(in srgb, var(--hud-magenta) 55%, var(--dc-pullquote-bg));` | the pull-quote panel | Pull quotes: the large magenta quotation mark. |
| S1 | Tabbed H3 tab bevel (`.section.dc-tabbed > h3:first-child`) (`components/section.css`) | `inset 0 1px 0 rgba(255, 255, 255, 0.18), inset 0 -1px 0 rgba(0, 0, 0, 0.22), inset -1px 0 0 rgba(0, 0, 0, 0.12);` | `inset 0 1px 0 color-mix(in srgb, #fff 18%, var(--dc-section-accent)), inset 0 -1px 0 color-mix(in srgb, #000 22%, var(--dc-section-accent)), inset -1p…` | the tab's own accent fill | H3 section tabs (Variant Gallery Section chassis "Tabbed, H3"): the 1px bevel lines. |
| S2 | Chapter-opener section shadow (`::after`) (`components/section.css`) | `background: rgba(0, 0, 0, 0.28); clip-path: polygon( 0 0, calc(100% - var(--dc-chapter-opener-clip-tail)) 0,` | `background: color-mix(in srgb, #000 28%, var(--wall-tone)); clip-path: polygon( 0 0, calc(100% - var(--dc-chapter-opener-clip-tail)) 0,` | the brick wall | Labelled chapter openers: the shadow down the section's right and bottom. |
| N1 | Credits colophon shadow (`dc-native.css`) | `box-shadow: 2pt 0 0 rgba(0, 0, 0, 0.28);` | `box-shadow: 2pt 0 0 color-mix(in srgb, #000 28%, var(--wall-tone));` | the brick wall | Credits page: the colophon panel's right-edge shadow. |

**Removed outright:** the AP chip's soft `3px 3px 6px` shadow (K4). A blur fades to transparent by definition, so it has no opaque equivalent. The chip keeps its hard 2px shadow.

## Not converted

| What | Why | Status |
|---|---|---|
| `.dc-cover-page` composite (`data.css`) and `--dc-cover-meta-border` | Built from four stacked translucent radial gradients, a scanline gradient and an SVG noise overlay. Converted layers would each be opaque and hide the ones beneath, so there is no faithful opaque version. | **Unused** by every book (catalog status `unused`). It is the test's only exemption. Rebuild it before any book uses it in a PDF/X build. |

## Where it changed (measured)

Each book was built before (last commit, `823b964`) and after, rendered at 50 dpi and compared pixel by pixel; a pixel counts as changed if any channel moves by more than 12/255. Page counts and layout are unchanged in both books: 132 and 232 pages. Every change is a colour change, and none is larger than 0.7% of a page's pixels.

### Design guide: 49 of 132 pages changed

Largest single-pixel changes first (`max` is the largest channel difference, in 0–255):

| Page | Pixels changed | Max |
|---|---|---|
| 90 | 0.1% | 115 |
| 106 | 0.06% | 115 |
| 115 | 0.06% | 115 |
| 12 | 0.04% | 115 |
| 88 | 0.15% | 100 |
| 123 | 0.08% | 100 |
| 122 | 0.0% | 100 |
| 75 | 0.62% | 92 |
| 33 | 0.11% | 56 |
| 53 | 0.28% | 54 |
| 2 | 0.16% | 51 |
| 91 | 0.05% | 46 |
| 111 | 0.2% | 44 |
| 118 | 0.06% | 43 |
| 55 | 0.03% | 37 |

All changed pages: 2, 12, 18, 24, 25, 29, 33, 38, 50, 52, 53, 54, 55, 56, 57, 73, 74, 75, 76, 77, 78, 79, 80, 81, 88, 90, 91, 96, 97, 98, 100, 101, 104, 106, 110, 111, 112, 113, 115, 116, 117, 118, 119, 121, 122, 123, 125, 126, 128

### Field Guide: 146 of 232 pages changed

Largest single-pixel changes first (`max` is the largest channel difference, in 0–255):

| Page | Pixels changed | Max |
|---|---|---|
| 130 | 0.02% | 110 |
| 124 | 0.14% | 94 |
| 134 | 0.4% | 92 |
| 136 | 0.03% | 92 |
| 129 | 0.18% | 84 |
| 125 | 0.37% | 78 |
| 122 | 0.36% | 61 |
| 135 | 0.22% | 61 |
| 123 | 0.08% | 61 |
| 133 | 0.07% | 61 |
| 131 | 0.06% | 61 |
| 127 | 0.04% | 61 |
| 132 | 0.14% | 60 |
| 126 | 0.13% | 60 |
| 128 | 0.01% | 60 |

All changed pages: 1, 2, 3, 29, 36, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 163, 164, 165, 166, 167, 169, 170, 171, 172, 173, 174, 175, 176, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 224

Spot-checked by eye: the largest changes are AP chips (no soft blur), skill-card body shadows, sticker and tab bevels, and tape dashes. Before and after crops are visually the same. The tape dash colour measured identical: `(221, 61, 51)` in both.

## PDF/X result

Field Guide, built with `--format pdfx --pdfx-flavor x1a` on gutterpress 0.11.15-alpha.1 (`dtrpg` preset):

| | Before (alpha wall and CSS) | After (this change) |
|---|---|---|
| Pages | 232 | 232 |
| Pages with live text | 43 | **210** |
| Text pages flattened to an image | 175 | **8**: pp. 3, 4, 7, 8, 10, 12, 13, 64 |
| Pages with no text in any build | 14 (art pages and the 4 closing blanks) | 14 |

The 8 pages still flattened carry the book's own alpha art, listed below. Every other text page keeps live, embedded fonts, so the k-only rewrite reaches its body text.

## Remaining transparency: the books' own art

These come from the book's own content, not this package. A page that places one of these images is still flattened in PDF/X-1a.

Measured on the Field Guide (dc-op-manual): 25 of the 30 images its chapters place have a real alpha channel. Its own stylesheets use no transparency.

| Image | Placed in |
|---|---|
| `images/chapter-02/augmerc.png`, `etherlock.png`, `gutterdruid.png`, `technosorcerer.png`, `wirephreak.png`, `scavenger.png`, `monkey-gunner.png` | chapter-02 specialty chapters, chapter-01 |
| `images/cysu.png`, `etlock.png`, `gutdru.png`, `proxy.png`, `streetwarden.png`, `techsorc.png`, `wf.png` (specialty icons) | chapter-01, specialty chapters |
| `images/blue-bot.png`, `image-everything.png`, `rabbit-walking.png`, `redpan.png` | chapter-01 |
| `images/chapter-00/a-team-logo.png`, `creaturepunk.png`, `neonrabbit.png` | chapter-00 |
| `images/chapter-03/Sluggernaughts.png` | chapter-03 |

There are two fixes, and both belong to the book:

- **Flatten each image onto its background.** The usual choice for cutout art that sits on a fixed place on the wall, but a cutout that moves with reflow will show a rectangle of wall that doesn't line up with the wall behind it.
- **Export with PDF/X-4** (live transparency) if the printer accepts it. DriveThruRPG asks for X-1a or X-3.

## Checklist

- [ ] Design guide: Variant Gallery, chapter openers, ch.5 components: shadows read as shadows, tints unchanged.
- [ ] Field Guide: a skill-tree spread (cards, AP chips, path stickers), a pull quote, a tape divider, the credits page.
- [ ] `bun test`: *paint nothing transparent (PDF/X-1a)* passes.
- [ ] PDF/X build: pages without alpha art keep live text (`pdftotext`).
