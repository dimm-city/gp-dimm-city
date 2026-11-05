# Print transparency inventory

What in this package is translucent, what is pre-composited, and how a PDF/X build treats each. The historical record of the 1.7 pre-composite pass (every translucent value it replaced, and the measurements) is kept at the end.

**The decision.** Translucent artwork is allowed by design: the shadows, lifts, bevels and tints that make a component sit on the wall are translucent, so the brick darkens under them. The cost is accepted: in a PDF/X build every page that carries any of it prints its artwork (rules, fills and shapes included) as one 300 DPI picture, and the file grows with it (the design guide's PDF/X is 75.5 MB against 11.4 MB plain). `pdfx.transparency: preserve-text` keeps the text of those pages live, so fonts, search and the K-only black rewrite are unaffected. What stays opaque is text: a translucent glyph cannot be kept live and flattens its page whole. Nothing here asks a page to stay vector.

## The model today: `pdfx.transparency: preserve-text`

PDF/X-1a, the format DriveThruRPG accepts, carries no transparency. Gutterpress's `pdfx.transparency: preserve-text` (0.11.23 and later; the design guide's manifest sets it, and a book that uses this package should) handles that page by page:

- A page with no transparency stays vector.
- A page with translucent **artwork** is split: its artwork is rasterised at 300 DPI (`pdfx.rasterDpi`) and its text is kept live on top, so the fonts stay embedded, `pdftotext` still reads it, and the `pdfx.blackText: k-only` rewrite still reaches its small text. On that page, rules, fills and shapes are raster, and text sits above every piece of artwork.
- A page whose **text** is translucent (opacity, a blend mode, a soft mask, a translucent `text-shadow`, or a `filter` on an element that holds text) cannot keep its text live and is flattened whole; the build names the page and the cause.

So translucency is allowed in artwork and forbidden in text. The package's styles follow that, and three tests enforce it (`test/conventions.test.js`): *keep text opaque (PDF/X-1a)*, *put a filter only on a ::before or ::after layer*, and *use no repeating gradient (PDF/X)* (PDF/X drops repeating gradients). What preserve-text does and does not cover, measured on the design guide, is in [print-qualification.md](./print-qualification.md).

## Translucent today

All artwork: shadows, lifts, bevels and a smudge. Each darkens or tints what is under it, so the wall's texture reads through.

| What | Where | Value |
|---|---|---|
| Poster shadow `--shadow-ink` | `dc-palette.css`; the hard offset in `--shadow-poster`: every lede, the contents and credits panels, specialty cards, stat grids | `color-mix(in srgb, var(--ink) 28%, transparent)` |
| Soft lift `--shadow-soft` / `--shadow-lift` | `dc-palette.css`; under anything hung on the wall: sections (`--dc-section-lift`), cards, the outcome ladder, the specialty card | `color-mix(in srgb, var(--ink) 34%, transparent)` |
| Recess `--shadow-press` | `dc-palette.css`; the soft inset of anything sunk into the wall: the fiction cavity, the `lore` / `dm` / `choose` sheets | `color-mix(in srgb, var(--ink-dark) 42%, transparent)` |
| Section hard shadow `--dc-section-hard-shadow` | `dc-component-defaults.css`; the section's offset copy (`section.css`) | `color-mix(in srgb, var(--ink-dark) 82%, transparent)` |
| Sticker and path-chip shadows, the spray smudge, the dashed rule | `chrome.css` | 35% and 30% ink; 8% of `--dc-spray-bg`; 50% magenta |
| Pull-quote accent `--dc-pullquote-accent-soft` | `dc-component-defaults.css` | 15% of `--tint-magenta-rose` |
| AP-chip and outcome-key bevels | `cards.css`, `data.css` | 8–18% ink and paper |

A book that sets one of these tokens to an opaque colour loses nothing in print; one that sets a text colour translucent flattens that page whole.

## Pre-composited (opaque by design)

| What | Why |
|---|---|
| Every text colour | A translucent glyph flattens its page whole (above). |
| The brick wall `images/brick-wall.png`, the six stone walls `images/wall-N.png`, the ground `images/ground.png` | An `@page` background with alpha would put every page through the split, text-only pages included; an opaque tile leaves a page vector unless it carries other translucent artwork. Each is an opaque tile baked by `scripts/wall-tiles.py` or from `source-art/` (see *The wall* below); `--wall-tone`, the old tile average that shadows were mixed against, is gone. |
| The band and tab gloss | `--light-gloss`, a gradient with transparent stops, made Chromium write a type-1 shading PDF.js cannot read (1.10.2). The path banner, the card tab and the specialty card band pre-mix the same sheen into their opaque fills; the token stays for books that read it. |
| The tape divider's crimson dashes (`.dc-tape::before/::after`) | An ordinary gradient with opaque stops, tiled by `background-size`: a `repeating-linear-gradient` cannot be kept live and flattens the page whole. |
| The bolt heads on a `##` slip, a vibe sheet and a skill card (`page-templates.css`, `chrome.css`) | Opaque discs: an ink ring round a `--paper-stain` face, the slot a hard-stopped band of ink (an ordinary gradient with opaque stops). They replaced the slip's translucent tape. |
| The paper tints that remain (the tape's tan, the specialty mixes, the accent inks of the slate block and the Surreal definition) | `color-mix()` into the surface they sit on, at a share that holds a printable dot (1.10.2). Callout, section, faction, choice and entry surfaces are no longer tinted: they are white. |

## How to verify a book

1. `gutterpress build <book> --format pdfx`. The build lists the pages it split ("Pages … use transparency … flattened to a 300 DPI picture with its text kept live on top"), any page it flattened whole and why ("text drawn with transparency or blending"), and any text-free page (an art plate) it flattened whole. A split page is expected on every page that shows a shadow; a whole-page fallback on a page with text is a bug in the book's styles.
2. `pdffonts <book>-pdfx.pdf`: every font embedded, none Type 3 (a Type 3 font is a synthesised bold or a filtered subtree printed as a picture). The build's `pdf.print.embedded-fonts` check reports a font that is not embedded; silence means they all are.
3. `pdftotext -f N -l N <book>-pdfx.pdf -` on a split page prints its words. Compare with the plain `--format pdf` build: the only expected differences are word joiners and line-end hyphens.
4. Small text prints in black alone: the build's `pdf.print.black-text` check reports any page with dark four-colour text at 24pt or under; silence means none.
5. `bun test`: the three convention tests above pass.

## Remaining transparency: the books' own art

The Field Guide (dc-op-manual) places cutout art with a real alpha channel (25 of its 30 images; its own stylesheets use no transparency). With `preserve-text` that costs nothing: the art is rasterised with the page's other artwork at 300 DPI and the text stays live. Only a `flatten-page` build loses the page's text to it. A page that is nothing but art (a plate) is flattened whole in either mode, and loses nothing. The two fixes that used to be needed, flattening each image onto its background or exporting PDF/X-4, are no longer.

## Checklist

- [ ] PDF/X build: every page with text is either vector or split with live text; no page with text falls back to whole-page flattening.
- [ ] `pdffonts`: all embedded, no Type 3.
- [ ] `bun test`: *keep text opaque (PDF/X-1a)*, *put a filter only on a ::before or ::after layer* and *use no repeating gradient (PDF/X)* pass.
- [ ] Design guide: Variant Gallery, chapter openers, ch.5 components: shadows darken the wall under them, text is sharp over them.

## The 1.7 pre-composite pass (historical)

Before Gutterpress had `preserve-text` (#385), Ghostscript flattened any page that used transparency into one raster image: the page lost its live text and embedded fonts, and the k-only rewrite could not reach it. This package used transparency in 26 places (an RGBA brick tile with a blend mode, semi-transparent shadows, tinted fills and `opacity`), and on the Field Guide **185 of 232 pages** came out image-only. The 1.7 series made every one opaque: each colour was pre-composited with `color-mix()` into the colour the transparency produced on the surface it sat on, and the brick wall became an opaque tile. Most of those values have since been reverted to translucent artwork (the table above), and some components have been redesigned since; this section records the pass as it was made, so the books can still be checked against it.

### The wall

| | Before | After |
|---|---|---|
| Image | `images/brick-bg-01.png`, RGBA, 3.8 MB | `images/brick-wall.png`, RGB, 2.2 MB: the RGBA tile multiplied into `--bg` (`#c8c5bf`) and flattened |
| Rule | `background: var(--bg) url(brick-bg-01.png); background-blend-mode: multiply` | `background: var(--bg) url(brick-wall.png)`, no blend mode (`dc-native.css` §1; the guide's `.dg-stage`) |
| Look | | Same: design-guide wall pages differ by 0.15/255 on average |
| Note | | A book that changes `--bg` no longer tints the brick. The RGBA source is in `source-art/` (unpublished), with the bake recipe in `dc-native.css` |

`--wall-tone: #c1beb8` is the opaque tile's average colour. Shadows that land on the wall mix against it.

### Changes

| ID | Component | Before | After | Mixed against | What to look at |
|---|---|---|---|---|---|
| T1 | Poster shadow token `--shadow-poster` (`dc-palette.css`) | `rgba(0, 0, 0, 0.28)` | `color-mix(in srgb, #000 28%, var(--wall-tone))` | the brick wall | Every lede (chapter openers, How Abilities Work), the Contents and Credits panels, specialty cards, the Introduction section, stat grids. The shadow is now a flat tone instead of a darkened view of the brick: check it reads as a shadow, not a grey band. |
| T3 | `--dc-pullquote-accent-soft` (pull-quote right rule) (`dc-component-defaults.css`) | `rgba(230, 0, 122, 0.15)` | `color-mix(in srgb, rgb(230 0 122) 15%, var(--dc-pullquote-bg))` | the pull-quote panel (`--dc-pullquote-bg`) | Pull quotes: the thin right rule (design guide ch.5 Pull quote; Field Guide pull quotes). |
| T5 | `--dc-tape-border` (tape divider border) (`dc-component-defaults.css`) | `rgba(212, 18, 0, 0.60)` | `color-mix(in srgb, rgb(212 18 0) 60%, var(--dc-tape-bg))` | the tape fill (`--dc-tape-bg`) | Tape dividers (design guide ch.5 Tape, Variant Gallery Tape; Field Guide NPC tiers). |
| T6 | `--dc-outcome-name-opacity` default (outcome-ladder result names) (`dc-component-defaults.css`) | `--dc-outcome-name-opacity: 0.85;` | `--dc-outcome-name-opacity: 1;` | — | See O2: the 85% is now mixed into the colour instead. |
| C1 | Blockquote right rule (`dc-core.css`) | `border-right: 2px solid rgba(230, 0, 122, 0.18);` | `border-right: 2px solid color-mix(in srgb, rgb(230 0 122) 18%, var(--paper-stain));` | the blockquote fill (`--paper-stain`) | Plain `>` quotes and epigraphs: the thin magenta right rule. |
| C2 | Spray banner smudge (`.dc-spray::after`) (`components/chrome.css`) | `background: var(--dc-spray-bg); opacity: 0.08; }` | `background: color-mix(in srgb, var(--dc-spray-bg) 8%, var(--wall-tone)); }` | the brick wall | Standalone spray headings (`## … {.dc-spray}`): the faint bar under the banner. |
| C3 | Path sticker shadow (`.dc-sticker`) (`components/chrome.css`) | `box-shadow: 2px 2px 0 rgba(0, 0, 0, 0.35);` | `box-shadow: 2px 2px 0 color-mix(in srgb, #000 35%, var(--paper-cream));` | the path panel (paper cream) | Learning-path skill stickers (every skill tree): the small drop shadow. |
| C5 | Path title sticker shadow (`.dc-path-sticker`) (`components/chrome.css`) | `box-shadow: 1px 2px 0 rgba(0, 0, 0, 0.30);` | `box-shadow: 1px 2px 0 color-mix(in srgb, #000 30%, var(--dc-path-title-bg));` | the path title bar | The tier tag (e.g. AUG1) in each path banner. |
| C6 | Sticker tier reference text (`.dc-sticker-ref`) (`components/chrome.css`) | `color: inherit; opacity: 0.55;` | `color: color-mix(in srgb, currentColor 55%, var(--ink-dark));` | the sticker fill (`--ink-dark`) | The small number before each sticker name in path rows (e.g. "1" in "1 · PUNISHING COUNTER"). |
| C7 | Dashed rule (`hr`) (`components/chrome.css`) | `border-top: 1.5px dashed var(--hud-magenta); opacity: 0.5;` | `border-top: 1.5px dashed color-mix(in srgb, var(--hud-magenta) 50%, var(--paper-cream));` | a paper panel (paper cream) | Every `---` rule: gear lists, sidebar boxes, NPC entries (design guide ch.5 Dashed rule; Field Guide gear chapter). |
| C8 | Tape shadow (`.dc-tape`) (`components/chrome.css`) | `box-shadow: 1px 1px 0 rgba(0, 0, 0, 0.15);` | `box-shadow: 1px 1px 0 color-mix(in srgb, #000 15%, var(--wall-tone));` | the brick wall | Tape dividers: the 1px shadow. |
| C9 | Tape dash pattern (`.dc-tape::after`) (`components/chrome.css`) | `background: repeating-linear-gradient(90deg, var(--crimson) 0 6px, transparent 6px 10px); opacity: 0.85;` | `background: repeating-linear-gradient(90deg, color-mix(in srgb, var(--crimson) 85%, var(--dc-tape-bg)) 0 6px, var(--dc-tape-bg) 6px 10px);` | the tape fill | Tape dividers: the dashed crimson rule after the label. |
| K1 | Skill-card body shadow (`.dc-card-inner::before`) (`components/cards.css`) | `background: rgba(0, 0, 0, 0.28); clip-path: var(--dc-skill-body-shape);` | `background: color-mix(in srgb, #000 28%, var(--wall-tone)); clip-path: var(--dc-skill-body-shape);` | the brick wall | Every skill card: the offset shadow behind the body (all ten skill trees; Field Guide specialty chapters). |
| K2 | Skill-card corner mark (`.dc-card-body::before`) (`components/cards.css`) | `background: var(--dc-card-body-mark); opacity: 0.15;` | `background: color-mix(in srgb, var(--dc-card-body-mark) 15%, var(--dc-card-surface));` | the card surface | The faint tilted dash at a skill card body's top right. |
| K4 | AP chip bevel and shadows (`.dc-ap`) (`components/cards.css`) | `inset 0 1px 0 rgba(255, 255, 255, 0.15), 2px 2px 0 rgba(0, 0, 0, 0.10), 3px 3px 6px rgba(0, 0, 0, 0.08); text-shadow: 0 1px 0 rgba(0, 0, 0, 0.20);` | `inset 0 1px 0 color-mix(in srgb, #fff 15%, var(--dc-ap-bg)), 2px 2px 0 color-mix(in srgb, #000 10%, var(--dc-card-surface)); text-shadow: 0 1px 0 colo…` | the chip fill (bevel, text shadow) and the card surface (drop shadow) | Every AP chip: the top bevel line, the hard 2px shadow, the text shadow. The soft 6px blurred shadow is REMOVED (a blur is transparency by nature). |
| O1 | Outcome key bevel (`.dc-outcome-key`) (`components/data.css`) | `inset 0 1px 0 rgba(255, 255, 255, 0.12), inset 0 -1px 0 rgba(0, 0, 0, 0.18);` | `inset 0 1px 0 color-mix(in srgb, #fff 12%, var(--row-color, var(--ink))), inset 0 -1px 0 color-mix(in srgb, #000 18%, var(--row-color, var(--ink)));` | the key's own fill | Outcome ladders (Variant Gallery Outcome ladder; skill cards with outcome tables): the 1px light top and dark bottom lines on each roll key. |
| O2 | Outcome result name (`.dc-outcome-key .dc-outcome-name`) (`components/data.css`) | `color: var(--dc-outcome-name-color); opacity: var(--dc-outcome-name-opacity);` | `color: color-mix(in srgb, var(--dc-outcome-name-color) 85%, var(--row-color, var(--ink))); opacity: var(--dc-outcome-name-opacity);` | the key's own fill | Outcome ladders: the small result word under each roll (TRIUMPH, SUCCESS…). |
| O3 | Pull-quote mark (`.dc-pullquote::before`) (`components/data.css`) | `color: var(--hud-magenta); opacity: 0.55;` | `color: color-mix(in srgb, var(--hud-magenta) 55%, var(--dc-pullquote-bg));` | the pull-quote panel | Pull quotes: the large magenta quotation mark. |
| N1 | Credits colophon shadow (`dc-native.css`) | `box-shadow: 2pt 0 0 rgba(0, 0, 0, 0.28);` | `box-shadow: 2pt 0 0 color-mix(in srgb, #000 28%, var(--wall-tone));` | the brick wall | Credits page: the colophon panel's right-edge shadow. |

**Removed outright:** the AP chip's soft `3px 3px 6px` shadow (K4). A blur fades to transparent by definition, so it has no opaque equivalent. The chip keeps its hard 2px shadow.

### Not converted

Nothing. The one item left translucent at first, the unused `.dc-cover-page` composite (stacked translucent gradients with no opaque equivalent), was removed, and the transparency test now runs with no exemption.

### Where it changed (measured)

Each book was built before (last commit, `823b964`) and after, rendered at 50 dpi and compared pixel by pixel; a pixel counts as changed if any channel moves by more than 12/255. Page counts and layout are unchanged in both books: 132 and 232 pages. Every change is a colour change, and none is larger than 0.7% of a page's pixels.

#### Design guide: 49 of 132 pages changed

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

#### Field Guide: 146 of 232 pages changed

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

### PDF/X result

Field Guide, built with `--format pdfx --pdfx-flavor x1a` on gutterpress 0.11.15-alpha.1 (`dtrpg` preset):

| | Before (alpha wall and CSS) | After (this change) |
|---|---|---|
| Pages | 232 | 232 |
| Pages with live text | 43 | **210** |
| Text pages flattened to an image | 175 | **8**: pp. 3, 4, 7, 8, 10, 12, 13, 64 |
| Pages with no text in any build | 14 (art pages and the 4 closing blanks) | 14 |

The 8 pages still flattened carry the book's own alpha art, listed below. Every other text page keeps live, embedded fonts, so the k-only rewrite reaches its body text.
