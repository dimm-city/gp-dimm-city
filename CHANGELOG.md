# Changelog

All notable changes to gp-dimm-city are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/) and the project uses
[Semantic Versioning](https://semver.org/). The release workflow refuses to
cut a version that has no `## [X.Y.Z]` heading below.

## [Unreleased]

### Changed

- **Tests and the guide build run on Gutterpress 0.11.23-alpha.6.** The dev
  dependency moves from 0.11.20-alpha.3, three releases behind, to the 0.11.23
  line the 1.10 release targets; `engines.gutterpress` is unchanged. The design
  guide's manifest uses 0.11.23's flat shape: `chapters:` (was
  `source.files`), no `page.tolerance` (the preset's), and no
  `validate.source.markdownlint` (the repo's `.markdownlint.jsonc` is found by
  walking up to the repository root).
- **Docs follow Gutterpress 0.11.23.** Vendored copies live under
  `extensions/npm/` (a book vendored earlier keeps `plugins/npm/` until its
  next `ext add` or `ext update`), the app adds an npm extension on Book
  setup's Extensions tab, and the README and `package.json` give the same minimum
  Gutterpress version, 0.11.20-alpha.3. The README's `ext list` sample shows
  1.9.0 with the badges in the order Gutterpress prints them.
- **The design guide and the snippets type the plain spellings** (`---`, `--`,
  `...`, `-`, `'`). `source.characters` findings on the guide drop from 367 to
  6, and the five snippets paste into a book with none.

### Removed

- **`size` from `styles/page-rules.css`'s `@page`.** Gutterpress 0.11.23
  writes the manifest's page size after every stylesheet and reports a `size`
  in a look as `printsafe/page-size-in-stylesheet` on every build. The sheet is
  the same 8.625 × 11.25 in; `--page-width` / `--page-height` stay as the
  look's record of it.
- **`gutterpress.tokensFile` from `package.json`.** Gutterpress 0.11.23 reads
  every enabled look's `:root` tokens and no longer reads the field.
- **The `lint` npm script and the `gutterpress lint` row in the design guide.**
  The command does not exist; the print-safety lint runs inside
  `gutterpress build` and `gutterpress validate`, and
  `gutterpress validate <book> --category source` runs the source checks
  alone.

### Fixed

- **`@outcome` rolls and ladder bands accept `--`.** `11--19` prints as
  11–19 and a ladder table typed that way is recognised; the `–` spelling
  still works. The character check asks for `--`, and Gutterpress 0.11.23's
  example books type it.

## [1.9.0] - 2026-10-26

### Changed

- **A specialty opens as a spread, and every learning path opens a page.**
  `.dc-specialty-intro` takes `break-before: left` and `.dc-specialty-art`
  `break-before: page`, so with the intro written first the plate faces it on
  the right (an intro longer than a page pushes the plate to the next left
  page). Every `.dc-learning-path` in a specialty takes `break-before: page`,
  and its banner sits flush with the page top. The plate's break moved from
  `chrome.css` to `page-templates.css` with the other specialty break rules.
  A book that wrote the plate before the intro should swap them. Until
  dimm-city/gutterpress#421 is fixed the live preview can put an intro on a
  right-hand page; the PDF places it correctly.
- **Design guide:** specialty specimens on doc pages (`.page.dg-doc`) keep
  their place in the flow (`guide.css` §8).
- **A panel's sub-headings sit one step below its title bar.** Under a 16pt
  `##` bar an `###` is 13pt; under a 13pt bar (`###`, or `##` with
  `{.dc-h3}`) an `###` is 11pt, and an `####` is 11pt in any panel. They
  were the bar's size or larger and read as a second title; books had stepped
  them down by hand with `{.dc-h4}`/`{.dc-h5}`, which still win. Panels with
  no bar, lore's captions and creature names keep their own. Sub-headings in a
  panel take `--space-lg` above, and an `###` in a column run takes the rail
  too (`section.css`; documented in design-guide ch. 6, Sub-headings in a
  panel). Books reflow: the Field Guide is four pages shorter.
- **Every column of an `@columns` run starts on one hang line.** The box
  that opens a column takes no top margin; Chromium kept it in the first
  column and after a forced break but dropped it at an unforced one
  (`page-templates.css`, COLUMN TOPS).
- **A definition of three paragraphs or more is set upright.** Italic stays
  for a short gloss; surreal keeps its italic (`data.css`).
- **A flavor line that leads into more text stays with it** (`break-after:
  avoid`), never alone at a page foot (`chrome.css`).
- **A wall heading sits on its text.** A `##`/`###`/`####` written straight
  on a page now lines up with the left edge of the paper sheet below it and
  sits on it with no gap, its dashed foot the sheet's top seam. Tags used to
  hang in 0.12in (every second one 0.3in) with a gap under them, so they
  looked misaligned and detached from their text (`page-templates.css`).
- **A run of prose in `@columns` is one sheet that does not split** across a
  page, and a `####`/`#####` inside it takes more room above than below and
  never ends a column (`page-templates.css`).

### Removed

- **`--dc-page-slip-offset`**, the hang-in of wall tags, which no longer hang
  in. A book that set it can drop it.

### Added

- **`--dc-specialty-intro-h3-color`**: the intro's `###` headings (and their
  underline) in each specialty's own colour. It defaults to `--blood`, and
  every `.dc-specialty.<name>` sets it to its `--spec-ink`, the text-safe ink
  (5.6:1 to 10.3:1 on the heading's cream band across the Field Guide's eight
  specialties).

## [1.8.2] - 2026-10-25

### Changed

- **The binding margin is DriveThruRPG's 0.5in, no longer 0.75in.**
  `--binding-margin` (`styles/dc-palette.css`) and so the spine-side margin of
  `@page :left`/`:right` is 0.5in on the sheet, which has no bleed at the
  spine, so 0.5in from the trim: the minimum DriveThruRPG states for text and
  non-bleeding art at the binding edge, and the value the gutterpress `dtrpg`
  preset's `page.gutter` carries. The 0.75in dated from the Field Guide's first
  layout (February 2026), where it arrived with a generic "gutter at least
  0.75in" review heuristic under a comment that itself said 0.625in; no
  DriveThruRPG rule asked for it. The text column grows from 7.25in to 7.5in,
  so every book reflows. A book that set `page.gutter: 54` to match the old
  margin should drop it and inherit the preset's 36pt: with the margin at
  0.5in, a 54pt gutter fails `pdf.print.safe-margins` on every binding edge.
  The design guide's page-geometry table, `docs/css-architecture.md` (which
  also showed a stale `--page-margin: 0.5in`; it is 0.625in) and the
  `dc-native.css` margin-box arithmetic (180 x 54pt) say the same.

## [1.8.1] - 2026-10-16

### Fixed

- **The page clip guard is scoped in one selector.** `.page` clips its
  horizontal overflow (a guard against Chromium's whole-document
  shrink-to-fit) except on a page holding pinned or bleed art. That exception
  was a second rule resetting `overflow-x: visible`, which Gutterpress's
  `printsafe/page-containment` check cannot see, so every build warned. The
  guard is now `.page:not(:has(.gp-bleed, .gp-pin, .gp-behind,
  .dc-specialty-art, .dc-full-page))`: the same pages clip, and the warning is
  gone.

## [1.8.0] - 2026-10-16

### Changed

- **The specialty catalog is a two-page spread of equal cards.** On
  `@page specialty-catalog` the cards are a two-column grid (it was wrapped
  flex rows, which the preview paginated differently from print). The left
  page holds the title, four cards and Dualist; the right page a `@lede`,
  four cards and Generalist. Dualist and Generalist span both columns as
  dense cards (portrait beside the text). Every one-column card is one size
  (3.15in, with a 0.7in portrait) and both full-width cards another (1.7in,
  with a 1.2in-wide portrait). **List Dualist fifth and Generalist last, and
  put the right page's `@lede` right after Dualist**: the cards keep the
  book's order, and whatever follows Dualist opens the right page (a literal
  `break-before: page`, which the preview honours too). Measured in the
  preview at the sheet's own size: the Field Guide's catalog ends 0.46in and
  0.41in above the foot of its two pages, the design guide's 0.29in and
  0.41in. The `--dc-card-grid-row` minimum now holds every one-column card
  to one height; new tokens: `--dc-card-grid-row-wide`,
  `--dc-card-grid-item-span`, `--dc-card-grid-media-wide`.
- **No number chip on a specialty card's portrait.** The `01`–`10` index chip
  and `--dc-specialty-card-index` are removed.

- **A chapter opener's pages carry the folio and chapter chip** (#12).
  `@page chapter-start` dropped both footers, and because a named page covers
  every page its box spans, an opener that ran onto a second page printed
  that page unnumbered too, so authors ended openers with `@page` to get the
  numbers back. Chromium cannot drop the folio on the opener's first page
  alone, so the suppression is removed: every opener page is numbered, the
  first included, with its chip in the chapter's colour like any page. The
  `chapter-start` named page is gone; the page word and its styling stay.
- **The brick wall tile is 900px wide instead of 2550px** (#1), which is
  600 DPI at its 1.5in repeat, twice the 300 DPI print bar. The package's
  unpacked size falls by 1.6 MB, and the wall looks the same in print.
- **Print qualification for `preserve-text` PDF/X** (#43). The design guide
  now builds its PDF/X with `pdfx.transparency: preserve-text`, and
  `docs/print-qualification.md` records the measured result: the pinned
  versions, a component table with crops, and the limits authors need to
  know (opaque text, no `filter` on text, text above artwork, 300 DPI
  artwork, `pdfx.flattenPages`).

- **Depth, recess and light, now that translucency prints.** Components get
  a soft, translucent lift off the wall (`--shadow-lift`) under their hard
  contact shadow: section panels (`--dc-section-lift`), path banners, skill
  cards and specialty cards. The section's hard shadow and the skill-card and
  `##` slip tape are translucent, so the brick reads through them. Recessed
  things sink: the fiction excerpt's cavity and the `lore`/`dm`/`choose`
  panels and title bars take a soft inset (`--shadow-press`). Title bands and
  skill-card tabs carry a top gloss (`--light-gloss`). All of it is `box-shadow` and
  gradients; a PDF/X build needs `pdfx.transparency: preserve-text`. A new
  convention test allows `filter` only on a `::before`/`::after` layer:
  Chromium prints the text of a filtered element as a picture.
- **A specialty card looks like its specialty's skill cards.** The card is
  now that specialty's path banner as a sheet: the name on the specialty's
  band colour, cut in the banner's title shape with its gloss and rule, and
  a paper sheet with an ink outline in the banner's silhouette. The thick
  top and left borders, the per-specialty card cut and the Augmerc override
  are gone. Removed tokens: `--dc-specialty-card-border`,
  `--dc-specialty-card-band-height`, `--dc-specialty-card-shadow`. New:
  `--dc-specialty-card-band-bg`, `--dc-specialty-card-band-fg`,
  `--dc-specialty-card-band-shape`, `--dc-specialty-card-pad-x`. A card's
  portrait floats on its frame (the image wrapper) rather than on the image.

- **Needs Gutterpress 0.11.20-alpha.3 or later**, the first with PDF/X
  `preserve-text`, which the translucent styles below print with. The
  requirement is in `package.json`'s `engines.gutterpress`: a Gutterpress
  that checks it (gutterpress#402) refuses to load this package and names the
  version to update to. Older Gutterpress versions ignore the field.
- **Shadows and tints are translucent again, for books that opt in to
  Gutterpress's `pdfx.transparency: preserve-text`** (Gutterpress #385). The
  poster shadow (`--shadow-ink`, so the skill-card body shadow and the section
  drop), the sticker and path-chip shadows, the rule divider, the spray smudge,
  the pull-quote accent, and the AP-chip and outcome-key bevels are
  `color-mix(…, transparent)` again instead of being pre-mixed onto one
  surface, so a shadow on the brick wall darkens the brick instead of painting
  a flat tone. The AP chip's soft `3px 3px 6px` shadow is back. Text colours
  stay opaque: a translucent glyph prints fully opaque on a split page. The
  wall tile stays opaque. `--wall-tone` is removed (nothing uses it). The
  convention test *paint nothing transparent* becomes *keep text opaque*, and
  its repeating-gradient check is kept as its own test.
  - A book that keeps Gutterpress's default (`flatten-page`) and builds
    PDF/X-1a gets more pages flattened to an image than with 1.7.2: set
    `pdfx.transparency: preserve-text` in the book's manifest. Requires the
    Gutterpress release that ships that option.
- **Lixdu is never faked bold.** Lixdu has one face, regular, but chapter
  chips, folio chips, outcome rolls, block and card titles and headings asked
  for a bold weight, so Chromium synthesized one, which prints as a Type 3
  font that Gutterpress's PDF/X `preserve-text` split cannot keep. Every rule
  that sets `--font-display` now sets `font-weight: 400` (a convention test
  enforces it), and headings set `font-synthesis-weight: none` so `**bold**`
  inside a heading prints in Lixdu's own stroke. That text is slightly thinner
  than the synthetic bold.
- **A continuation card's tab draws its "continued" triangle** as a small
  inline SVG in the title's colour, instead of a `▸` character. No Dimm City
  font has that glyph, so Chromium borrowed one from a system font and printed
  it as a Type 3 font; on the Field Guide that was the last one, and it made
  its page fall back to whole-page flattening under `preserve-text`.

## [1.7.4] - 2026-10-15

### Changed

- **Proxy and Wirephreak swap colours.** Proxy now takes the magenta (the more
  purple of the two: `--brand-magenta` accent, `#9a1896` mid, `#8a1a90` dark,
  a deep-magenta title band with a cream tier chip) and Wirephreak the electric
  indigo (`--signal-indigo` accent, `#2f2290` mid, `#1e0f50` dark, an indigo
  band and chip). Each keeps its own shapes and band register (Proxy's facet
  plane, Wirephreak's ticked LED rule). The Surreal definition block keeps its
  indigo-black surface, now read from `--wirephreak-dark`.
- **The design guide and tests run on Gutterpress 0.11.20-alpha.3** (a
  development dependency only: the published package does not depend on
  Gutterpress). Its preview repeats a table header only where print does
  (dimm-city/gutterpress#398). The tests drop core's new `data-name` block
  stamp before comparing markup, as they already drop its source stamps, and
  read a column's alignment from `data-align`, which core now writes in place
  of markdown-it's inline `text-align`.

## [1.7.3] - 2026-10-15

### Fixed

- **A specialty opener's art runs to the bottom edge of the sheet** (#54). The
  image sits in a paragraph wrapper that stayed at its content height, so the
  image's `height: 100%` resolved to nothing and it kept its own aspect ratio,
  and core's in-flow image cap (`max-height: calc(var(--gp-content-h) - 4px)`)
  held it 4px under the page besides. On the Field Guide's 8 openers the art
  stopped 6.36pt (0.04in) short of the 810pt sheet, inside the bleed band, with
  only the plate's dark backdrop under the gap. The wrapper now fills the
  plate and the plate's image drops the cap (the plate is exactly one sheet
  and clips its own overflow), so the art reaches every edge. Gutterpress
  0.11.20's art safe-area overlay no longer flags those pages.
- **The release run's tarball tests have a timeout sized for `npm pack`.** The
  first of them runs `npm pack`, which on a busy runner can take longer than
  bun's default 5s test timeout; that failed the 1.7.1 release run before it
  published.

## [1.7.2] - 2026-10-15

No package rule counts a book's rows or blocks any more: a threshold like
"four blocks or fewer" or "12 rows or more" only holds for the content it was
measured on, so it belongs in that book's own sheet.

### Removed

- **The long-choose-table rule from 1.7.1** (`.dc-section-choose > table:has(>
  tbody > tr:nth-child(12))`), which never reached npm. Tables are kept whole,
  as in 1.7.0. A book with a
  table taller than the page under its heading lets that one split from its own
  sheet, e.g. `.dc-flaws > table { break-inside: auto; }` for the Field Guide's
  Flaw table.
- **The panel break rules that counted blocks** (`components/section.css`,
  "Where a panel may break"): a panel of four blocks or fewer kept whole, and a
  panel of five or more keeping its 2nd block with its 3rd and its last block
  with the one above. A panel now splits where the page ends; its heading still
  stays with the block under it, and text still keeps 3 orphans and 3 widows.
  A book that wants the 1.7.1 behaviour copies the three rules into its own
  sheet; the design guide does (`design-guide/styles/guide.css` §7).

### Changed

- **A skill card's opening** is written `:first-child, :first-child + *`
  instead of `:nth-child(-n+2)`. Same rule: the flavor line and the block
  after it stay with what follows.

## [1.7.1] - not released

Never published: its release run failed in the test job (the tarball test
timeout fixed in 1.7.3), and 1.7.2 removed its one change before the next run.

### Fixed

- **A long table of choices splits between rows.** A table of 12 rows or more
  in a `choose` section (`@flaws`, `@ideals`, `@section choose`) may now break
  between rows; each row is a whole option and the header repeats. At the 10pt
  floor the Field Guide's 19-row Flaw table no longer fit under its heading,
  so the whole table jumped to the next page, left the opening page empty and
  pushed the section's last two lines onto a third page. Shorter tables, and
  tables outside `choose` sections, still stay whole.

## [1.7.0] - 2026-10-15

A redesign pass by component family. A reader should know what kind of box they
are looking at from its silhouette, fill value and colour before reading a word,
and every variant is told apart in grayscale as well as in colour (value, edge
and label, never hue alone). Magenta is display punch only (chevrons, spray
titles, pull quotes, `ROLL THE DIE!`, the VAR chip, the default panel accent);
the other roles are HUD blue for player rules and look-ups, cyan on ink for the
Dream Master only, hazard yellow with ink for danger and choices, blood and rust
for harm and cost, violet for the world, fungi green for the organic. The
constitution is revised to match: §II adds the colour roles and the grayscale
rule, §V and §VI set a 10pt type floor, and §VII describes the new
components.

A second pass, from review of 1.7.0-alpha.1, set a 10pt type floor for all
text, took every word off the brick wall, tied shape to meaning and added a
little grit.

### Added

- **`@page specialty-catalog`**: the specialty catalog is a designed two-page
  spread. It opens on a left page; the title, the lede and four cards fill the
  left page and six the right, in aligned rows of equal height. Each card is a
  poster: portrait on top in an ink mat cut to its specialty's silhouette,
  name, tagline, pitch and an index chip. Snippet *Specialty Catalog Page*.
- **`@callout location` and `> [!LOCATION]`**: a place written up, drawn as
  the origin callout's document (dog-eared corner, torn foot, worn rubber
  stamp) in map teal: cool paper, a teal rail, a deep-teal stamp.
- **`@definition lucid` and `@definition surreal`**: the two roll states drawn
  as opposites. Lucid is a light, machined, upright sheet in a blue frame;
  Surreal is an inverted violet-black sheet with a skewed torn edge,
  off-register inks and a leaning headword.
- **No text on the wall.** On wall pages free-standing text gets a substrate
  with no markup: a `#` title is an accent banner, `##` a pasted paper slip
  (accent rail, dashed foot, tape), `###` a plain slip, `####` and below a
  label slip, and loose paragraphs, lists and quotes share one paper sheet per
  run. A bare `@section` is a paper sheet; flavor lines and the spec tweak sit
  on paper strips; the Citizen File running head is an amber tab. Tokens
  `--dc-page-slip-*`, `--dc-page-sheet-pad`, `--dc-page-title-ink`,
  `--dc-flavor-bg`.
- **Grit**, vector and opaque, on edges and labels only: chipped corners,
  tape strips, misregistered second-ink rules (`--dc-band-reg` on the tech
  specialties), worn stamp rings, torn feet, a staple on the procedure plate.
- **`--dc-accent-ink`**: the text-safe ink of the component you are in. Every
  alert, section kind, block, card, faction, entry, table and specialty sets
  it; chapter accents flow through.

### Changed

- **Type floor: 10pt for all text**, chips, tabs, tier pills, AP chips,
  badges, stamps, folio and chapter chips, stickers and labels included. New
  token `--fs-floor` (10pt); `--fs-h6` is the floor (was 9pt). Chrome that
  grew was refitted so nothing wraps or clips; a five-step sticker chain may
  now wrap to two rows.
- **ROLL THE DIE! takes the colour of its component** (deep magenta in a
  magenta panel, blood in a blood box, the specialty's ink on a skill card).
  `--dc-roll-the-die-color` is replaced by `--dc-accent-ink`.
- **Fiction is a cavity.** `@fiction-excerpt` is an aged page sunk into a
  ragged hole in the wall: a dark torn rim, a hard shadow down the top and
  left, a lit lip at the bottom and right, deeper on a chapter opener. New
  tokens `--dc-fiction-depth`, `-depth-bg`, `-cavity`, `-lip`, `-rim`,
  `-hole`; `--dc-fiction-lift` and `-lift-bg` are removed.
- **Shape carries meaning.** Player rules and look-ups are machined chamfers;
  Dream-Master-only boxes are file folders (the `dm` section's tab carries the
  words, replacing its chip); danger and enforcement are sign plates; lore and
  cabal long asymmetric slashes; fiction, backstory, cult and flaws torn;
  choices ticket notches; gear tags; magic facets; organic boxes wobble. The
  eight alerts, every section kind, block, choice card, faction, entry, table
  and all ten specialties are re-cut to match, and every clipped edge is
  padded clear of its cut by 2pt or more.
- **Folio and chapter chips** are fixed-height boxes with their type centred,
  on recto and verso. The chapter chip is a stamped coupon in the chapter's
  colour, replacing the dashed outline.

- **Alerts: eight registers, eight silhouettes.** Each has its own fill value,
  edge and label. Bodies are italic, as before; the example's is upright.
  - note: the calm HUD-blue panel with a blue rail, as before.
  - warning: a light cream hazard sign: a yellow and black stripe rail, an ink
    frame and a yellow caution-tape label. It signals consequence.
  - dm: an ink slab with a cyan rail and a cyan chip. It signals the Dream Master
    only.
  - vibe: a barely violet flat sheet in one violet edge, italic, with no
    rail: the world's voice, not a slab.
  - origin: warm paper, a rust rail, a dog-eared corner and a crimson rubber-stamp
    label: second-person backstory.
  - location: the origin's document in map teal: a place written up.
  - visit: a fungi-green signpost with a map-pin label: a place.
  - example: a cyan rail with a taped-on label.
  New tokens `--dc-alert-frame`, `-label-bg` and `-label-pad` carry the frame
  and label chrome. The hazard rail, the dog-ear fold, the spray stencil line and
  the NPC card foot are drawn in vector (borders and clip-path), because
  gradients are dropped or rasterised in PDF/X. The DM and visit bodies are
  semibold (reversed type).
- **Section kinds read from their bar and sheet.** Panel keeps the solid accent
  bar on cream (magenta by default, the only kind a chapter re-themes); reference
  a pale HUD band; lore a deep violet bar over a lilac sheet; dm an ink bar with a
  cyan rule, a cyan rail and a Dream Master chip (cyan on ink is now the Dream
  Master's alone), with a strip of its own when it has no heading. `choose` is a
  printed form, not a panel: a paper sheet a hair lighter than cream, an ink
  edge, no bar or cut corners, an ink title over a double rule, heavy ink tick
  boxes, dotted write-in rules and a yellow *Choose* stamp. The title bar is
  one rule reading new tokens (`--dc-section-bar-mix` / `-bar-tone` / `-bar-fg` /
  `-bar-rule` / `-bar-rule-sub`, and `--dc-section-flag`); each kind sets them
  instead of repainting the bar, and so does the catalog. A block's band reads
  `--dc-block-title-rule` and `--dc-block-tag`.
- **Blocks: three registers.** `@block panel` stays HUD blue; `slate` is an ink
  body under a blood band with a stamped *Binding* tag (not magenta, not the
  Dream Master's cyan); `shard` is light zine paper with a torn foot and a taupe
  label strip, no accent hue.
- **Choice cards say which choice they are.** A Flaw is blood with a cracked edge,
  an Ideal HUD blue with a steady tablet shape, a Dream violet with a rising edge,
  each with a one-word chip and a kind-tinted quote. The kind sets
  `--dc-choice-accent`, `-surface`, `-tint` and `-kind`, and a card inside them
  reads them (the choice chrome is scoped to `@flaws`/`@ideals`/`@dreams`, so a
  gear entry or a faction keeps the plain card).
  The card name is the first `####`; the docs and snippets say `####` throughout.
- **Factions have their own silhouettes.** Megacorp a hard blue rectangle with a
  cyan-edged band, cabal violet with long corner cuts, cult blood and torn, enforcer
  an octagon with a hazard-stripe band and a yellow name label. The bands are
  vector (solid inset shadows; the enforcer's tape is a skewed dashed border), not
  gradients. New tokens `--dc-faction-surface`, `-band` (a box-shadow list),
  `-band-height`, `-pad-bottom`, `-badge-shape`, `-title`, `-title-bg` and
  `-title-pad`.
- **A creature's stat line is a chip.** The first line of an `@npc-stat`'s primary
  stat paragraph is set 12pt bold, cream on the block's colour (`::first-line`, no
  markup); the rest falls under it as a small-caps tag.
- **Entry cards differ by silhouette, surface and badge.** Gear is a hang tag
  (a paper card in a heavy ink frame, an eyelet, a rust rail), an augment a spec
  chip (a stepped notch, a cyan rule), treasure a gem (an octagon cut, a facet), a
  vehicle an industrial plate (an inner seam, a yellow badge), a drug a
  prescription label (the one rounded shape, an *Rx · Drug* pill). Every mark is a
  solid fill, border or clip, so it prints as vector in PDF/X (no gradients). New
  tokens `--dc-entry-radius`, `-ornament`, `-orn-inset`, `-orn-bg`, `-orn-border`,
  `-orn-clip`, `-orn-z`, `-frame` and `-badge-bg`, `-badge-fg`, `-badge-shape`,
  `-badge-radius`. Chips and tags never hyphenate. Field labels share one chip: effects are a solid teal frame
  with a +, side effects a dashed blood frame with a – (`--dc-field-edge-width`,
  `-edge-style`).
- **Catalog entries are kept whole.** An entry never splits across a column or a
  page (the catalog itself still splits between entries), and its title bar is a
  ledger band with an INVENTORY chip instead of an accent bar.
- **Procedure is off the wall.** `@procedure` is an instruction plate: a cream
  sheet with an ink frame and a hard shadow, a solid HUD-blue number strip, step
  text in ink and ruled dividers (`--dc-steps-accent`, `--dc-steps-surface`).
- **At-a-glance has a hierarchy.** The tile is a reversed label band over a large
  value, with an ink frame and a hard shadow (`--dc-at-a-glance-accent`, `-value`).
  The outcome ladder's chip column is `max(130px, 26%)` (`--dc-outcome-key-col`)
  so long band names wrap cleanly.
- **Definition is a dictionary page,** not a tinted note: cream, a heavy rule over
  it, the term set first as a blue headword; the shape is `none` by default.
- **The lede is the opening statement.** Upright semibold ink type at 13pt on a
  light panel (lighter than the wall) with a heavy accent rail and an ink foot rule
  (`--dc-intro-color`, `-size`, `-weight`, `-style`, `-rail`, `-rule`). Flavor is a
  rail and no box, in ink-dark. Contents and credits ledes keep body size.
- **NPC flavor lines** are a ruled line, not a box.
- **Chrome.** `.dc-tag` is an inline chip with a hard edge and an ink hairline
  (`--dc-tag-bg`, `-fg`, `-border`); `.dc-tape` is masking tape with torn ends and
  ink edges (`--dc-tape-shape`); `.dc-spray` is a stencil tag with a stepped edge
  and a dashed stencil line (`--dc-spray-stencil`) against the chevron's deep
  banner; the spec tweak fits one line; the NPC sidebar is a contact card with a
  blue ID band and an ink strip foot.
- **Specialties are told apart.** The title bands (path banner and specialty-intro
  title) are each specialty's own signal colour with its own register: an LED rim
  and a rule of LED dots on the tech specialties, a facet plane on the magic ones, a
  hazard-tape rule on Streetwarden, a torn bottom edge on Technosorcerer and Gutterdruid, all
  drawn as solid fills, dotted/dashed borders and clip-paths (no gradient, so they
  survive PDF/X). New tokens `--dc-band-rule`, `-rule-h`, `-tick`, `-tick-style`,
  `-tick-w`, `-rule-skew`, `-rule-bleed`, `-facet`, `-facet-width`,
  `-facet-clip` and `-rim`, and `--dc-path-code-*`, `--dc-path-chip-*`,
  `--dc-path-note-rail`. A path with no subtitle is the band alone.
- **The tier pill is the specialty's own.** `--dc-tier-bg`, `-fg` and `-edge`,
  set per specialty, replace the bronze, gold and silver by position (the
  `--tier-*` tokens are gone).
- **AP chips differ in grayscale.** Free is an unlit LED, a grey lens with a hollow
  lamp and an ink edge (it was the same blood red as increased), reduced is pale
  blue with a drawn down triangle, increased blood with a drawn up triangle (CSS
  shapes, not font glyphs), VAR deep magenta (cream on the bright one was 4.06:1),
  special amber with cream type.
- **Augmerc and Wirephreak swap colours.** The Augmerc is signal cyan (a
  teal-black LED rule with cyan ticks, deep-teal ink) and the Wirephreak deep
  magenta (a cyan LED rule with ink ticks); `--augmerc-*` and `--wirephreak-*`
  swap values. Their silhouettes are unchanged.
- **Proxy and Technosorcerer swap looks; Generalist leaves violet.** The
  Proxy is now electric indigo (`--signal-indigo`) with the tech-and-magic
  register (a centre gate notch, an LED rule, a facet plane), and the
  Technosorcerer takes the scorch-orange landfill-and-magic register (a burnt
  corner, a torn foot, a scorch patch, aged-paper card) that suits ritual on
  scrap. `--proxy-*` and `--technosorcerer-*` swap values to match, and every
  skill card, learning path, intro and specialty card follows. Violet is the
  world's colour (lore, vibe, cabal, treasure), so the Generalist is cool slate
  (`--crystal-slate`). The Technosorcerer's band is a shade lighter so ink on it
  holds 4.5:1.
- **New neutrals.** `--paper-form` (the `choose` sheet) and `--paper-zine` (the
  fiction excerpt and shard sheets).
- **Ink coverage under 280%.** Measured through the build's own PDF/X
  conversion: `--ink` is `#1e1d1c` (278%, was 284%) and `--ink-dark` is
  `#2f2622` (266%, was 271%). `--deep-rust`, `--fungi-rot` and six
  specialty darks are lifted to 268% or less. Every palette and identity token
  carries its measured CMYK and TAC. No raw `#000`/`#fff` remains in a
  `color-mix()`.
- **Pagination.** A panel of four blocks or fewer stays whole; a long panel
  never opens or ends on a single block; panel and callout text keeps three
  orphans and widows; skill cards split between ability rows.
- **Lore, dm and choose are sunk into the wall.** No drop shadow: the wall's
  top edge casts a hard shadow down over the sheet's top and its title bar, and
  a light lip runs along the bottom and right (`--dc-section-recess`, `-depth`,
  `-shade`, `-lip`). Panel and reference still hang. `@flaws`, `@ideals` and
  `@dreams` are choose sections, so they are recessed too.
- **Edges are solid; the dash is kept where it is the object.** Clip-path and
  border colour tell kinds apart. Solid now: the choose edge, the flaw card
  edge, the vibe edge, the example rail and its label, the cult rail, the shard
  rule, the skill-card continuation tab, procedure and definition dividers,
  `hr`, the stat-strip cells, the vehicle seam, the gear price tag, the NPC
  stat rule and the human-callout foot. Still dashed or dotted: the warning's
  hazard rail and the enforcer's band, the `##` slip foot and `.dc-spray`
  stencil line, write-in rules on a form, the origin stamp ring, the
  side-effect field frame, link and ROLL THE DIE! underlines, the LED ticks.
- **Labels are raised.** Every label stands off what it sits on with a hard
  2px ink shadow (`--dc-label-shadow`), or an inset bottom-and-right edge where
  a clip-path would cut it (`--dc-label-edge`). Every alert label is now a chip
  (`--dc-alert-label-bg` defaults to cream; `--dc-alert-label-shadow`).

### Fixed

- **No text on the wall from `@flaws`, `@ideals` or `@dreams`.** A headless one
  dropped its sheet on the assumption it held only cards; one that also holds
  prose or a table keeps its sheet.
- **`> [!NOTE]` alerts** from the gutterpress-gfm-alerts extension (`.gp-alert`)
  are drawn as the matching callout (note, tip and important as the note;
  warning and caution as the warning) instead of bare text on the wall.

- The learning-path title band lines up with the path frame's top-right cut
  for every specialty: it spans the frame and is cut from the same point list,
  where it stopped 12px short.
- The design guide's heading specimens sit on paper, not on brick.
- The folio and chapter chips are 0.225in tall with their type centred in
  them, and sit 0.025in below the text block (page margins are unchanged from
  1.6.3). The chapter chip takes the chapter's colour (named pages `dc-chip-<hue>`) and lost a
  stray notch.
- The `dm` section's folder tab stays with its box when the section splits
  across a page; it had left cyan type on grey paper.
- The page-level wall-text rules skip components (`[class*="dc-"]`), so a
  `@procedure`, `@lede` or `@toc` placed straight on a page keeps its look.
- Reversed type is semibold: slate and Surreal bodies, skill-tab names. Cream
  on the default magenta bar is 4.7:1 (`--dc-section-bar-mix` 90%); outcome
  band names are at least 4.5:1.
- Flaw, Ideal and Dream cards differ in grayscale (edge style, fill value,
  silhouette depth); `reference`, `lore`, `panel` and `dm` title bars differ
  in treatment, not only colour.
- A wrapped learning-path sticker chain never ends a line on its arrow.
- Heading slips keep with what follows, prose sheets take orphans and widows
  of 3, and `###`/`####` slips hang offset (`--dc-page-slip-gap`,
  `-slip-offset`, `--dc-heading-gap`).
- Tests guard the 10pt floor, page-level components, the Lucid/Surreal
  variants, opaque paint and repeating gradients.
- The tape divider's crimson dashes print in PDF/X: they were a repeating
  gradient, which PDF/X drops, and are now an ordinary gradient tiled every
  10px (#41).
- A learning-path banner contains its slanted band rule, so the overhang no
  longer widens the page and a book builds without `allowShrink`.

- **Contrast and type.** The special AP chip (ink on amber, 3.5:1), the tier pills
  (the accent failed 4.5:1 for 9px type on the magenta and orange bands), the learning-path
  subtitle (ink-smoke on `--paper-stain`, 3.4:1), the magenta title band (cream on
  bright magenta, 3.6:1; now the Wirephreak's) now pass 4.5:1, and the NPC flavor line is a ruled line on the paper instead of italic on a grey box. The DM alert
  body is set at the 10pt floor instead of 9pt.
- **A chapter no longer repaints the alerts.** The Dream Mastery chapter's override
  turned every alert grey-brown and rust in Part 2; the alert identity now survives
  re-theming. Its DM panel heading was ink on ink (an empty-looking bar) and is
  readable.
- **Names stay on one line where they can.** An NPC name in a two-column run,
  a catalog entry name and TECHNOSORCERER on its specialty card no longer wrap
  mid-name or orphan a letter.
- **Empty strips are gone.** A learning path with no subtitle or stickers is the
  band alone, not a band over an empty well.
- **The design guide's choice-card snippets work.** They wrote `### Name`, which
  core does not turn into the card heading (only the first `####` is); they now
  write `####`. The Part 2 Fodder description sat between the quote and the stat
  lines and was set as a stat line; it is now inside the quote.
- **README example.** The author-override example set `--dc-alert-accent`, a token
  that does not exist; it now sets `--dc-section-accent` on `.dc-section-panel`.
- A skill card no longer leaves two lines and empty cream on a page, and a
  page-level callout no longer pulls the previous block onto its page. The
  guide's sample book has no stub or one-card pages left.
- The guide's Introduction page sets its story in `@fiction-excerpt`.

### Removed

- **The highlight skill-card variant** (`#### Name | Tier | highlight`, `@skill {.dc-highlight}`) is gone, and the guide no longer describes a capstone skill: the game has none. A third `|` part in a skill heading is ignored.

## [1.6.3] - 2026-10-12

Content and markers by default, overrides when wanted: the defaults now do more,
so a book writes fewer `.dc-avoid-split`, `.dc-snug`, `{.dc-chevron}` and `gp-*`
classes, and every override that stays is documented and has a token a book can
set from its own CSS.

### Changed

- **Each kind of box has its own shape.** As the skill cards change shape per
  specialty, every section variant and boxed component now cuts its own corners,
  so its silhouette says what it is:
  - panel: top right (unchanged); reference: all four, small; lore: top left and
    bottom right, long; dm: top right and bottom left; choose: bottom right;
    catalog: both top; `@npc-stat`: both right; citizen walkthrough: top left.
    The title bar follows the panel's top corners. New tokens
    `--dc-section-cut-tl`, `--dc-section-cut-br`, `--dc-section-cut-bl` sit
    beside `--dc-section-clip` (the top-right cut).
  - callouts and alerts: top left and bottom left; `@card`: bottom left;
    `@faction`: both bottom; entry cards (`@gear` and its kinds): all but the
    bottom left; fiction excerpt: all but the top left; `@definition`: all but
    the top right. Each reads a `--dc-<component>-shape` token; a catalog's
    ruled entries keep the square box.
  - Shapes are paint only: no page breaks move (the Field Guide and SysOps
    paginate as before).
- **Fiction is set into the page.** The fiction excerpt reads as a recess, not a
  card: a hard inner shadow along the top and left and a light edge bottom and
  right (`--dc-fiction-shadow`), under its cut corners. The chapter-start excerpt
  drops its raised offset shadow (and the 6px right margin kept for it) and keeps
  its two ink rules.
- **Lore is violet, not brass.** `@section lore` and `@chapter lore` drop the
  amber bars on aged and light-brown paper: violet bars (`--brand-violet`) on the
  panels' clean cream, italic sub-heads in violet.
- **No tan boxes.** A treasure entry is violet on cream (rail, kind word and
  name in `--brand-violet`) instead of amber on the gold tint, and `@definition`
  sits on a pale HUD-blue tint of cream that matches its cyan rail instead of the
  orange tint.
- **ROLL THE DIE! stands out more.** Its underline is dotted, and its colour is the
  brand's deep cyber-magenta (`--brand-magenta-deep`) instead of `--blood`, which
  sat close to the body ink and is also the colour of other bold text. It keeps AA
  contrast on every paper (7.0:1 on paper-cream). A book that wants the old colour
  sets `--dc-roll-the-die-color: var(--blood)`.
- **A creature stays whole by default.** An `@npc-stat` with no `####`, or one (a
  species and its one variant), is one creature, read at one glance: it keeps its
  padding inside its box and moves to the next page rather than splitting, as
  `.dc-avoid-split` did. `.dc-avoid-split` on one is now redundant. A block with
  two or more `####` entries is unchanged (it breaks between entries, never inside
  one). `--dc-npc-stat-break-inside: auto` lets one split.
- **A catalog splits by default, and an explicit override still wins.** A
  `@section catalog` reads its own token, `--dc-catalog-break-inside` (default
  `auto`), because a run of entries kept whole leaves the foot of the page before
  it blank. An author's `.dc-avoid-split` on it still keeps it whole, as it always
  did, and so does `--dc-catalog-break-inside: avoid` from a book's CSS. A
  container's `--dc-section-break-inside` does not reach a catalog.
- **Keeping a box whole is a token per component.** `--dc-section-break-inside`,
  `--dc-catalog-break-inside`, `--dc-npc-stat-break-inside`,
  `--dc-skill-card-break-inside` and `--dc-faction-break-inside` are declared at
  `:root` (`avoid` or `auto`), and each component reads its own. `.dc-avoid-split`
  is now a setter of them (and of `--dc-section-edge: 0px`, which keeps a whole
  section's padding inside its box), so a book writes the same declarations for
  one box from its own sheet (`#core-loop { --dc-section-break-inside: avoid;
  --dc-section-edge: 0px; }`). A sheet that sets only the first still keeps the
  section whole; the second keeps the pagination identical to the class. Sections,
  skill cards and factions render as before. The skill card's `:not(.dc-avoid-split)`
  guards on its keep-with-next chains are gone: a card kept whole is unaffected by
  chains until it is taller than a page.
- **The space under paragraphs and list items is `--dc-flow-gap`.** `.dc-snug` is
  now a setter of it (0.04in), and a book sets it on any box. Unset, each
  component keeps its own spacing, so nothing changes until it is set. A
  `revert-layer` fallback in the template layer hands the margin back to the
  component while the token is unset.
- **Entry art has a default.** An image with no class inside a `@gear` entry
  floats right at half the card (`--dc-entry-art-width`, 50%), as
  `{.gp-right .gp-medium}` does. An image with no class on its own line under the
  credits colophon is a band across the foot of the sheet, the page's full width
  and `--dc-credits-art-height` (2.75in) tall, cropped to fit. Both read only an
  image with no class, so a `gp-*` class an author writes still wins (the plugin's
  layer outranks core's).
- **A front-matter title is a chevron by context.** The plugin writes `.dc-chevron`
  on the `h1` straight under `@page intro`, `credits` and `contents`, so those
  titles need no `{.dc-chevron}`; the class still works on any other heading and
  is not doubled where it is written. The snippets for the three pages no longer
  write it.

### Fixed

- **A ladder table keeps what the author wrote on it.** `{#id .class}` after a
  table of the five bands, outside a skill card and in one, was dropped with the
  table; it now lands on the `.dc-outcomes` element, with any other attribute.
- **`@procedure` keeps the attributes on its line.** The wrapper renders nothing,
  so `@procedure #steps .tight` lost its id and class; they now land on the list
  (the first, when there are several, so an id stays unique).

### Removed

- **Two selectors that matched nothing in the design guide or either book:**
  `.dc-skill-card:only-child` and `.dc-sidebar:empty`, and the
  `.dc-card.dc-faction.dc-avoid-split` rule the faction token replaces. The 94
  selectors that match nothing in the two books were checked against the design
  guide too: 79 are documented there (`.dc-stat*`, `.dc-tape`, `.dc-spec-tweak`,
  `.dc-npc-compact`, `.dc-img-float-*`, `.dc-sidebar`, the `@npc-stat` stat-line
  rules and others), and the rest are element baselines, a rule a test asserts, or
  the loose-list half of a live selector, so they stay (see
  `docs/cleanup-backlog.md`).

### Added

- **README: "Author overrides".** One section for the supported overrides: core's
  `gp-*` classes (a pointer to the Gutterpress guide), each plugin modifier with
  what it does and the token that does the same from a book's CSS,
  `@page-break`, `@columns`, `{#id}`, and the coming `[data-name]` hook. The
  "what are you writing" tables no longer list `.dc-avoid-split`, `.dc-snug` or
  `.dc-sidebar` as if ordinary content needed them, in the README and the design
  guide.
- **The catalog names every class an author can write.** `components.yaml`:
  `modifier:` takes a class or a list, `description:` is one line for every
  modifier and author-facing class, and `.dc-h3` … `.dc-h6`, `.dc-chevron`,
  `.dc-flush`, `.dc-spray`, `.dc-spec-tweak` / `.dc-no-top`, `.dc-sidebar` and the
  image floats are entries with their modifier, for the app's completions. The
  integrity test checks both.

## [1.6.2] - 2026-10-12

### Changed

- **`@gear` is the one item marker; the kinds are words on it.** `@gear augment`,
  `@gear treasure`, `@gear vehicle` and `@gear drug` give the cybernetic, magic
  item, vehicle and drug cards, each with the look and the small kind word it
  had. A bare `@gear` is general gear. The entries still share one card
  family and one check (an entry with no name, or with two, is reported), and a
  word that is not a kind is reported and read as general gear. A run still
  needs an `@end-gear` only after its last entry, and `@section catalog` takes
  `@gear <kind>` entries as it took the old markers. Entry cards now carry
  `data-gear="<kind>"`.
- **`@field specs` is the one SPECS box.** A `**SPECS:**` paragraph inside an
  entry, an `@npc-stat` or a skill was already that field; it is now the only
  way to get the box, since `@callout gear` drew the same one.
- **The card footer is tagged by the plugin alone.** The `blockquote:last-of-type`
  fallback beside `.dc-card-footer` is gone from `section.css`; the plugin
  always tags the footer.
- **A specialty's last learning path clips its card shadows.** The poster
  shadow hangs 6px below a skill card; when the last card of a specialty ended
  in the last 6px of a page, that overhang alone opened an empty page before
  the next chapter. `.dc-specialty > .dc-learning-path:last-child` now clips
  its block overflow (`overflow-y: clip; overflow-clip-margin: 8px`), so a book
  no longer needs its own rule for it.
- **A field may split between lines, as the callout it replaced did.** `.dc-field`
  no longer has `break-inside: avoid` and sets `orphans: 2; widows: 2`, so the
  label chip stays with the first two lines of its text and no single line is
  left alone at either end. A short field still stays whole. The 30 SPECS boxes
  that were pushed whole to the next page no longer cost a book pages.
- **Skill card text never leaves one line alone at a page edge.** Paragraphs,
  list items and ability text inside `.dc-skill-card` set `orphans: 3; widows: 2`.
  Chromium keeps the orphans and drops the widows when a paragraph is too short
  to satisfy both, so the body's 2 + 2 let a three-line paragraph split 2 + 1;
  with 3 it moves whole. Cards still split by default.
- **A panel's bottom edge is paint, not layout, so it cannot open a page.**
  Since 1.4.1 the `::before` surface and `::after` shadow layers extended below
  the box by `--dc-section-edge` (a negative `bottom`). That extension is
  positioned content, and when a panel ended in the last pixels of a page, such
  as a `@section reference .dc-snug` pulled back to fit, Chromium fragmented it
  onto a page of its own holding only the panel's bottom rule: on a book's last
  chapter, the page DriveThruRPG needs fully blank. The layers are now exactly
  the box, and the edge and the shadow's 3px hang below it as `box-shadow`
  copies pushed down by `--dc-section-edge`, with the clip-path reaching down
  to match, so a panel looks as before and opens no page.
- Comments in the plugin, stylesheets, catalog, snippets and docs that described
  removed code, files or behaviour are gone or rewritten. No declaration or
  behaviour changed with them.

### Removed

- The `data-break-inside="avoid"` attribute on skill cards, outcome ladders and
  card sub-lists. Nothing read it since the pagination polyfill was removed;
  break control is the CSS `break-inside` rules.
- `@augment`, `@treasure`, `@vehicle`, `@drug` (and their `@end-` forms):
  write `@gear <kind>`. They are tombstoned in `components.yaml`.
- `@callout gear` and `> [!GEAR]`, with `.dc-gear-callout`: write `@field specs`.
  `components.yaml` has a tombstone for each.

### Moving from 1.6.1

| Before | Now |
|---|---|
| `@augment` … `@end-augment` | `@gear augment` … `@end-gear` |
| `@treasure` … `@end-treasure` | `@gear treasure` … `@end-gear` |
| `@vehicle` … `@end-vehicle` | `@gear vehicle` … `@end-gear` |
| `@drug` … `@end-drug` | `@gear drug` … `@end-gear` |
| `@callout gear label="SPECS"` … `@end-callout` | `@field specs` … `@end-field` |
| `> [!GEAR]` | `@field specs` |

Any other `@callout gear label="…"` becomes `@field specs label="…"` for a
one-paragraph box, or `@callout note` (or `warning`) for a longer note. The old
spellings are not recognised any more: a marker line prints as text, and
`@callout gear` reports an unknown variant. A book that sets its own rule on
`.dc-gear-callout` should move it to `.dc-field-specs`.

## [1.6.1] - 2026-10-12

### Changed

- **Faction cards split across pages.** A `@faction` profile runs to half a page
  or more; kept whole, a chapter of factions left half-empty pages. It now
  splits between paragraphs like an entry; the name stays with its first lines,
  and `.dc-avoid-split` on the marker keeps one whole.
- **The outcome ladder keeps its table's header.** The two header cells
  (`Roll | Result`, `d20 | Repair Time`, …) now sit in the ladder's label bar
  over the two columns, instead of being dropped for a fixed "Outcomes" label.
  A table with an empty header, and `@outcome`, still say "Outcomes". The bar
  is the same height, so no page moves.
- **ROLL THE DIE! is set in the text, not as a chip.** The phrase (and ROLL A
  DIE!, ROLLS A DIE!, ROLLING THE DIE!) keeps the font and size of the text
  around it and is bold, in a contrasting colour (`--dc-roll-the-die-color`,
  default `--blood`), and underlined.

### Removed

- `--dc-roll-the-die-border`: the phrase has no border any more.

## [1.6.0] - 2026-10-12

### Added

- **The d20 ladder is recognised by its bands.** A two-column pipe table whose
  first column holds exactly the five standard bands (`20`, `11-19`, `6-10`,
  `2-5`, `1`, in either order) is drawn as the coloured outcome ladder, in a
  skill card or anywhere else, whatever its headers say (`Roll | Result`,
  `Result | Effect`, empty). A band is read however it is typed (`11-19`,
  `11 – 19`, `**20**`) and shown as `11–19`. Any other set of bands (six bands,
  a split at 10) stays a plain table. Before, only a `Roll | Outcome` header
  triggered it, and only inside a skill card.
- **`@roll-table`**, a neutral random-table component for tables with equal
  bands (`1-4`, `5-8`, …): a caption with a die chip (`die=d20`, any `dN`) and
  a `label`, a mono range column, equal-weight rows and no tier colours. The
  table inside stays a plain pipe table and is never read as a ladder.
- **Four kinds of text, as words on `@section`:** `reference` (a look-up:
  HUD blue, a pale title band, tight rows), `lore` (the world: brass on aged
  paper, a long shard corner, italic sub-heads), `dm` (behind the screen: an ink
  bar with a Dream Master chip on a cold body) and `choose` (a choice the
  player writes on the Citizen File: a lighter form sheet, dotted write-in
  rules, tick boxes, a "Your choice" chip, in the chapter's accent). Each is a
  panel plus one class that sets the panel's tokens, with no marker of its own.
  New tokens `--dc-section-tab`, `--dc-section-tab-bg` and `--dc-section-tab-fg`
  draw the chip. `@flaws`, `@ideals` and `@dreams` are now `choose` sections
  with their own class.
- **`@callout example`**, the one spelling for a worked example: a dashed cyan
  edge, a taped-on label, upright text. It replaces `@block shard label="Example"`
  and `**Example:**` paragraphs.
- **`@faction megacorp | cabal | cult | enforcer`**, an organization's profile:
  a card whose rail and kind badge take the kind's colour (`--dc-faction-accent`,
  `--dc-faction-badge-fg`). `label="…"` names a badge of your own.
- **`@npc-stat compact`** for a small creature, a companion or a drone: no
  panel, a framed box, the two stat lines as chips side by side.
- **The stat strip.** A table with an `HP` column and a `Damage` column is set
  as a strip of labels and big numbers (a cell holding only a number is set large) wherever it sits, with no marker
  (`--dc-stat-strip-accent`, `--dc-stat-strip-value`). A creature inside a
  skill's ability text needs this: a section marker there would end the skill.
- **A chapter-start page with no fiction excerpt still opens like a chapter.**
  The `# Title` is a band in the chapter's accent and the paragraph under it is
  the lede (an `@lede` keeps its own look). A page with a fiction excerpt is
  unchanged.
- **`@definition` reads as a glossary** when it holds a run of `#### Term`
  entries: a small mono-caps term, a dashed rule between entries, and the block
  may split between them. A `---` inside is the same dashed rule.
- `| highlight` on a skill heading is documented as the capstone look (the
  card that pays off a path); it is not a new word.

- **Entry cards: `@augment`, `@treasure`, `@vehicle`, `@drug`.** Cybernetics and
  mods, magic items and relics, vehicles, and drugs and consumables each get
  their own marker, snippet and catalog entry. They share one card style family
  (`.dc-entry`) and each kind is a token setter on it (rail colour, name colour,
  surface, and a small kind word over the name), so the CSS stays small. Existing
  entry markdown (`#### Name`, a blockquote tagline, a `**SPECS:**` paragraph,
  prose) works unchanged inside them. An entry with no name, or with two names
  run together, is reported as a problem.
- **`@field`, and bold labels that mean it.** A labelled field with variants
  `specs`, `traits`, `equipment`, `effects`, `side-effects` and `requires`; the
  default label is the variant's name and `label="…"` replaces it. Inside an
  entry card, an `@npc-stat` and a `@skill`, a paragraph that opens with a label
  the books already write (`**SPECS:**`, `**Traits:**`, `**Equipment:**`,
  `**Effects:**`, `**Side Effects:**`, `**Requires:**`, `**Wirephreak Gear:**`,
  `**Cybersurgeon Instrument(s):**`, `**TECHNOENHANCEMENT:**`) becomes the same
  field, so books need no content change. The labels are one table in
  `plugin.js`.
- **`@section catalog`.** A panel for a run of entries that rules them instead of
  boxing them: each entry takes a rule in its own accent colour over it, so the
  hand-typed `---` between entries is not needed (one left in draws nothing).
  Write `@columns 2` under the intro as before.
- New tokens `--dc-entry-accent`, `--dc-entry-ink`, `--dc-entry-surface`,
  `--dc-entry-rail`, `--dc-entry-rule`, `--dc-entry-kind` and
  `--dc-field-accent`, `--dc-field-surface`, `--dc-field-fg`,
  `--dc-field-label-fg`.

### Changed

- **Skill cards split across pages by default.** A whole card is a third to half
  a page, so keeping each one atomic left most specialty pages holding one card
  and a third of the sheet empty. A card now splits at sensible places: it never
  opens with only its tab, an ability row is never cut, a lead-in stays with what
  it introduces, and the last block stays with the one above. `.dc-avoid-split`
  (written on the `@skill` line, as on a section) keeps one whole.
  `.dc-allow-split` is retired: it is the default.
- A table of five bands now shows its roll as `11–19` (an en dash) however the
  author typed it, and its tier and name come from the band.
- `@gear` is now an entry card (`dc-card dc-entry dc-gear`) and takes a `####`
  name as well as `###`; its rules moved from `section.css` to the new
  `styles/components/entries.css`. `@callout gear label="SPECS"` still works.

### Removed

- `@glossary` and `.dc-terms`: write `@definition` (a run of `#### Term` entries,
  or `**Term** — gloss` paragraphs).
- `@sidebar-box` and the `--dc-sidebar-box-*` tokens: write `@definition` (a
  `####` heading, `---` and body make the same box).
- `@section aside`: write `@callout`.
- `@sidebar` and `--dc-sidebar-surface` / `--dc-sidebar-border`: write
  `@callout note .dc-sidebar`. `.dc-sidebar` remains as a float placement only.
- `@block codex` (`.dc-codex`): write `@section reference` for a look-up panel, or `@block panel` for a small box inside a section (a section cannot nest).
- `.dc-allow-split` on `@skill` (see above).

## [1.5.0] - 2026-10-12

Needs **Gutterpress 0.11.17 or later**: that core resolves the variant
words on `@section`, `@page` and `@chapter` that this release declares.

### Added

- **Page and chapter words.** `@page chapter-start`, `intro`, `credits`,
  `contents` and `citizen-file` write `dc-page-<word>`; `@chapter rules`, `lore`,
  `citizen-file` and `specialty` write `dc-chapter-<word>` and set the section
  colour of the chapter (rust, brass on aged paper, magenta-deep, blue-dark).
  A location only sets tokens; it never draws a component's chrome. Snippets
  and catalog entries for each word.
- **Panel edge tokens.** `--dc-section-clip` (the chamfer, 18px) and
  `--dc-section-rail` (the rail, 5px) are read by the panel's `::before` and
  `::after`; `--dc-section-gap` and `--dc-section-grow` set the space below a
  panel or flat section and let a flat section fill a flex-column page.
  `--dc-intro-gap`, `--dc-intro-pad-bottom` and `--dc-toc-rail-y`,
  `--dc-toc-rail-x`, `--dc-toc-shadow`, `--dc-toc-badge` do the same for the
  lede and the contents card.
- **Section variants: `@section panel`, `@section flat`, `@section aside`.**
  A bare `@section` is now core's plain box and this package styles nothing on
  it; the look comes from a word after `@section`. `panel` is the card the bare
  section used to be (cream substrate, accent rail, clipped corner, shadow,
  title bar). `flat` is the rail on a plain host with no card, the look the
  intro section and the credits colophon share (its extra shadow is the new
  token `--dc-section-drop`). `aside` is an inset note, built
  on the `@sidebar-box` treatment with its rail on `--dc-section-accent`.
  Needs Gutterpress with page, chapter and section variants. A test now fails
  if any rule in `styles/` matches `.section` without a `dc-` class.
- **The section components are words on `@section`.** `@npc-stat` is
  `@section npc`, `@fiction-excerpt` is `@section fiction`,
  `@citizen-walkthrough` is `@section walkthrough`, `@card-grid` is
  `@section cards`, and `@flaws`, `@ideals` and `@dreams` are
  `@section flaws`, `@section ideals` and `@section dreams`. Each pair writes
  the same classes. The card-like ones (`npc`, `walkthrough`, `flaws`,
  `ideals`, `dreams`) now also carry `dc-section-panel`. `@gear` and
  `@outcome` are not sections, so they have no word.
- **`.dc-avoid-split`.** Keeps a section whole: it moves to the next page rather
  than splitting. Sections now split by default.
- **`@fiction-excerpt` has its own look.** Aged paper (`--paper-aged`), no
  rail, no title bar, narrative leading, and the first image floats. On a
  chapter-start page (`@page chapter-start`) it takes
  the heavier opener edge, 2px ink rules and an offset shadow, so a book no longer
  needs its own rule for it. New tokens: `--dc-fiction-rule`,
  `--dc-fiction-shadow`.
- **`@gear` is styled.** A card with an orange rail; the name, the italic
  tagline and the bold price line are picked out by shape, and a trailing
  `@callout gear label="SPECS"` sits a gap below the body. It was a bare card
  before.
- A callout directly before a panel now has a gap between them.
- Snippets `section-panel`, `section-flat` and `section-aside` for the snippet
  picker, and catalog entries for the three variants and `.dc-avoid-split`.

### Changed

- README: books commit the manifest pin, not `plugins/npm/` (Gutterpress ignores the
  downloaded copy and restores the pinned version on a fresh clone); installing a
  version removes the old copy, so the manual `git rm` step is gone.
- Documentation: a "Pick a section" table (in the README and at the start of the
  design guide) maps what you are writing to the marker; `components.yaml` now
  lists every marker, section, page and chapter word and modifier with its
  snippet, and names the replacement for each retired item (`@tabbed`,
  `@column-panel`, `@sidebar inset`, `.dc-plain`, `.dc-allow-split` on a
  section, the labelled opener); a new test fails when a declared word has no
  entry or snippet. `docs/` describes the section variants, the page and
  chapter words and the two rules that govern them. A spelling pass over the
  design guide, docs, catalog, snippets and comments fixed one mistake (a
  stylesheet comment).
- **Page templates are token-only.** The rules for the contents, credits, intro
  and chapter-start pages set `--dc-*` tokens on the components they adjust (the
  lede, the contents card, the flat section) and style only the page's own
  element and plain elements; the components read the tokens. The credits
  colophon's flex column is gone (its type size moves to the flat section's
  children, its growth and bottom gap to tokens) and the intro chevron's
  redundant margin and shadow resets are dropped. A test fails if a rule keyed
  on a page or chapter class declares anything but custom properties on a
  component.
- **Core's `@page full-bleed` and `.dc-full-page` are one page.** Both get the
  plate geometry and the package's `full` named page.
- **A bare `@section` no longer looks like a card.** Write `@section panel`
  where you want the card. A bare `@section` still groups its content and now
  has no surface, rail, shadow or title bar. The first heading in it is an
  ordinary heading.
- **`@section .dc-npc-stat`, `.dc-citizen-walkthrough`, `.dc-flaws`,
  `.dc-ideals` and `.dc-dreams` no longer get the card.** The card now comes
  from `.dc-section-panel`, which the marker and the word write beside the class.
  Use `@npc-stat` (or `@section npc`) and the like; the raw class spelling is a
  plain section.
- **The intro section and the credits colophon are `@section flat`.** The rules
  that matched `.page-intro > .section` and `.section.credits-colophon` now match
  `.dc-section-flat` on those pages, and set only `--dc-section-accent` and
  `--dc-section-drop`. Write `@section flat` in place of a bare `@section` under
  an intro lede and of `@section .credits-colophon`.
- **Sections split across pages by default.** Nothing in this package sets
  `break-inside` on a section any more, including inside `@columns` and for
  an `@npc-stat` with no `####` entries. Add `.dc-avoid-split` to keep one whole.
- `@card-grid` no longer sets its own surface, padding or `break-inside`; it is a
  bare wrapper with a top margin.

### Removed

- **The raw page spellings are no longer styled.** `@page .page-chapter-start
  .dc-chapter-start`, `@page .page-toc`, `@page .page-credits .dc-credits`,
  `@page .page-intro` and `@page .dc-citizen-file-page` still render their
  classes but get no template rules and no named page (so the footer, margins
  and masthead are gone). Write the word instead: `@page chapter-start`,
  `contents`, `credits`, `intro`, `citizen-file`. Book rules keyed on the old
  classes (`.page.page-chapter-start.dc-chapter-start.chapter-03 …`) key on
  `.page.dc-page-chapter-start.chapter-03 …`.
- **`.dc-allow-split` on sections.** Sections split by default, so there is
  nothing to allow. Delete it from `@section` and `@npc-stat` lines; add
  `.dc-avoid-split` where a section should stay on one page. `@skill
  {.dc-allow-split}` is a separate switch on skill cards and is unchanged.
- **`.dc-plain` and the `--dc-section-break-inside` token.** A bare `@section`
  is already plain. Write `@section` where you wrote `@section .dc-plain`. The
  `@columns` rule in `dc-native.css` that set the token, and the `@npc-stat`
  rules that only existed to flip it, are gone.
- **`.credits-colophon`.** See Changed: write `@section flat`.

- **`@tabbed` and `.dc-tabbed`.** The hung-tab section (the heading cut out
  as a tab above the panel) had no use in either book, and its two tokens
  `--dc-section-tab-overlap` and `--dc-section-tab-indent` go with it. Write a
  `@section panel`: its first heading prints as the bar across the top.
- **The labelled chapter-opener styling.** A `@chapter C.01` followed by
  `@page intro` no longer gets the stacked `C.01` badge, the chevron title or
  the clipped panel: the rules that keyed on
  `.chapter[data-chapter-label] > .page[data-page="intro"]` and the
  `.chapter-opener` badge are gone, with the `--dc-chapter-opener-*` tokens,
  `--fs-chapter` and `--augmerc-deep`. Gutterpress core still writes
  `data-chapter-label` and `.chapter-opener`; this package no longer styles
  them. Open a chapter with `@page chapter-start` and a
  `# Title`, as both books do. The design guide's chapter-opener, specialty
  overview and rules chapters now use that form.
- **`@sidebar .inset` and `@page .page-sidebar`.** The full-height rail pinned
  to a page edge, the template that reserved its column, and the tokens
  `--dc-sidebar-inset-column`, `--dc-sidebar-inset-gutter`,
  `--dc-sidebar-callout-accent`, `--dc-sidebar-callout-bg` and
  `--dc-sidebar-accent` are gone. `@sidebar` itself (the floated box) stays,
  and `@sidebar` no longer takes an `inset` variant word. For a short aside in
  the text flow, use `@sidebar-box`.
- **The forced 1.6 line height on the chapter-start page's paragraphs.** The
  rule `.page-chapter-start.dc-chapter-start p` reached every paragraph on the
  wrapper, including ordinary sections on the sheets after the title. Those
  paragraphs now take the book's normal leading. Set `line-height` in your
  own sheet if a chapter opener needs looser text.

## [1.4.1] - 2026-10-11

### Fixed

- **A splittable section that ends flush at a page foot no longer leaves a
  nearly blank page after it.** When a `.dc-allow-split` section (or an
  `@npc-stat` with `####` entries) filled its last page to the foot, its
  bottom padding, and the card edge and shadow that cover it, moved to the
  next page as a thin strip. The card's bottom edge now takes no layout space
  on those sections: the surface and shadow layers hang below the box into the
  margin, and the margin below grows by the same amount, so nothing after the
  card moves. Sections that cannot split are unchanged. An element with a
  top margin over 12pt (such as `.dc-tape`) directly after a splittable
  section now sits up to one padding closer to it.

## [1.4.0] - 2026-10-11

One way to set content in columns: Gutterpress core's `@columns N` …
`@column-break` … `@end-columns`. Everything else this package did with
columns is removed or now takes that marker. **This release needs
Gutterpress 0.11.17-alpha.6 or later**: that core draws the column hairline
(`--gp-column-rule`), reads a bare `@columns` as two, lets `@section`s sit
inside an `@columns` run, and no longer splits a keep-together section that
follows other content. Two rules here that only undid that last core
behaviour (on a single-creature `@npc-stat` and on a section after a
`.dc-intro` lede) are removed with it.

### Changed

- **`@columns` works inside a `@skill` card.** A `@columns 2` … `@end-columns`
  run (and any `@column-break` in it) used to end the card at the marker, so
  the columns and everything after them landed outside the card. They now stay
  in the card's body, in place.
- **`@card-grid`, `@npc-stat`, `@citizen-walkthrough` and the credits
  colophon take `@columns 2` inside them.** `@card-grid` no longer sets its own
  columns: write `@columns 2` around its cards (the grid keeps its chrome reset
  and card density). An `@npc-stat` keeps creatures whole and breaks between
  entries whether they sit directly in the block or in an `@columns` run in it
  (a one-creature block follows a section at a page foot without splitting, and
  the bar is never left alone above an empty first row);
  a walkthrough keeps the two-line heading height in its column runs. The
  credits snippet writes the colophon names in `@columns 2` instead of a
  `dc-colophon-grid` div.
- **The column gap and hairline are two tokens, set once.** `--gp-column-gap`
  (the gutter) and `--gp-column-rule` (a 1pt hairline) are set at `:root`
  instead of by rules on `.gp-columns-2` / `.gp-columns-3`. Three columns now
  use the same gap as two (0.15in, was 0.18in). The hairline needs the next
  Gutterpress; until then no column rule is drawn. `.dc-card-grid` and the
  credits colophon set `--gp-column-rule: none`, as they never drew one.
- The rules that let a section or a callout fragment inside a column run now
  match any run (`@columns N`, or a count class on a panel), not only the
  two- and three-column count classes; the guard on a page that was itself a
  column run (`@page .gp-columns-2`) is gone with that form.

### Removed

- **`.dc-two-col` (`@skill {.dc-two-col}`) is gone.** A card that wants columns
  wraps just that part of its body in `@columns 2`; the flavor line and sub-headers
  stay full width. Books that wrote the class should replace it.
- **`.dc-cards-two-col` is gone.** Written on a wrapper (typically
  `@specialty .augmerc .dc-cards-two-col`), it set every skill card inside
  two-column, which broke the layout of cards that should not be columned:
  short blocks split into one-line fragments, a lone line in the right
  column, list blocks divided unevenly. A wrapper no longer decides its
  cards' columns. A card that needs two columns says so itself with
  `@columns 2` inside it, and a section of running text uses core's
  `@columns 2`. Books that wrote the class should delete it from their
  `@specialty` lines; until they do it does nothing.
- **`.column-break`** (`---{.column-break}`, an `<hr>`): write core's
  `@column-break`.
- **`.dc-colophon-grid`**, **`.dc-at-a-glance-cards`** (a three-across grid;
  keep the `.dc-at-a-glance-card` cards and set them in `@columns 3`), and the
  `column-fill: balance` rule on `.gp-columns-2` / `.gp-columns-3` (it restated
  the CSS default).
- The `.gp-grid-2` / `.gp-grid-3` support added in 1.3.0: the float-containment
  default is a plain `:where(.section) { display: flow-root }` again, and the
  grid-row spans for a panel's header bar are gone. A long run of gear entries
  packs two-up in `@columns 2` inside a `@section .dc-allow-split`.
- **`@column-panel` / `.dc-column-panel` are gone.** Columns have one spelling,
  core's `@columns N`. Write a plain `@section` with the body in `@columns 2`;
  the heading and intro paragraph stay above the run, full width. Before:
  `@column-panel .gp-columns-2` … `@end-column-panel`; after: `@section` / `##
  Heading` / `@columns 2` … `@end-columns` / `@end-section`. The migrated
  panel looks like a normal `@section` card.

## [1.3.0] - 2026-10-11

### Changed

- **The die chip now covers every wording of the instruction and no longer
  disturbs the line it sits in.** Besides `ROLL THE DIE!`, the chip wraps
  `ROLL A DIE!`, `ROLLS A DIE!` and `ROLLING THE DIE!` (uppercase, as written;
  the text is never altered). It is redrawn as a stamped label (cream fill,
  blood-red lettering, magenta rule and offset shadow) set as a plain inline
  box, so a line holding a chip keeps the line height of the lines around it
  and a chip never splits across two lines. Headings are left as plain heading
  text. `--dc-roll-the-die-color` and `--dc-roll-the-die-border` work as before. (#18)
- **A run of cards or gear entries can pack two-up** (#15). Core's `.gp-grid-2` and
  `.gp-grid-3` did nothing on a `@section` or `@column-panel`: the plugin's
  float-containment default (`display: flow-root`) sat in a later cascade layer
  and beat core's `display: grid` at any specificity, so every card took a full
  row. The default now steps aside for the two grid classes, and the header bar
  and preamble paragraph of a grid panel span the first row.
  `@column-panel .gp-grid-2 .dc-allow-split` is the gear and item layout; the
  design guide's Gear section shows it.

### Fixed

- A heading word wider than its box now breaks instead of running under the
  next column or being clipped at the edge. This applies to `h1`-`h6` and the
  `.dc-h3`-`.dc-h6` looks in every context (a two-column run is about 3.4in
  per column), not only inside cards. Headings whose words fit are unchanged,
  and an author's soft hyphen (`&shy;`) still picks the break. (#13)
- In a loose bulleted list (blank lines between items) the `»` bullet no longer
  prints alone on a line above the item's text. A loose item's text is wrapped
  in a paragraph, so the bullet is now drawn on that first paragraph and sits
  inline with the first line, in alerts and callouts too. Tight lists and
  every other list render exactly as before. (#17)
- **`@npc-stat` blocks with `####` entries no longer split a creature across
  pages or columns** (#16). The block may now break between entries (so
  `@npc-stat .gp-columns-2` no longer jumps whole to the next page and leaves
  a large empty area), the title bar stays with the first entry, and each
  entry's name, stat lines and traits are kept together. Add `.dc-allow-split`
  for an unusually long entry. A block with no `####` is unchanged.
- The chapter opener's `# Title` is never split across two sheets: it keeps
  together and stays with the block after it, so a long opener moves the
  whole title to the next page instead of leaving one line of it at the
  foot of the page before. (#12)
- A callout label (`@callout gear label="SPECS"`, `[!NOTE]`, any variant) no
  longer sits alone at the foot of a column or page with its body in the next
  one: `.dc-alert-label` now carries `break-after: avoid`, which matters in the
  multicol runs where a callout is allowed to split. A `@column-panel` header
  bar can still be left at a page foot when its first block is not a
  paragraph; that is a Chromium limit (it ignores `break-after: avoid` on a
  `column-span: all` box), documented in `section.css`. (#14)
- **A split column panel that ends in an `@card` or `@outcome` shrinks to its
  content** (#15). Both drew a decoration with an absolutely positioned box,
  which stopped Chromium balancing the panel's last fragment: it ran the full
  page height, so the next panel could not start beneath it. The `@card` body's
  decorative tick is now the skill card's alone (it was never part of the
  `@card` primitive's tokens), and the outcome ladder's inner hairline is an
  inset shadow.
- **A column panel that ends flush with the page foot no longer spills its
  bottom edge onto an extra page** (#15). The panel's bottom padding and rule
  are painted as shadows below a box that ends with its content, so there is
  no trailing box edge to push to the next sheet. Same picture, same spacing;
  a neighbour with a larger top margin than the panel's bottom margin can now
  sit up to 10px closer, because the padding that used to sit inside the panel
  no longer adds to that gap.

## [1.2.0] - 2026-10-10

Requires Gutterpress 0.11.16 or newer (the desktop app or CLI): older
versions reject the `section: true` markers below and do not report a
mistyped `@callout` variant (`unknown_variant`).
Books pinned to an earlier gp-dimm-city are unaffected until re-pinned.

### Changed

- **Eleven plain wrappers are now declared in a `markers` table** instead of
  being hand-written in the plugin's state machine: `@sidebar`,
  `@sidebar-box`, `@definition`, `@specialty-intro`, `@specialty-art`,
  `@specialty-card`, `@gear`, `@toc`, `@lede`, `@glossary` and `@block`.
  Gutterpress core now parses, nests and closes them, and the editor lists
  them. The emitted elements and classes are unchanged; rendering the design
  guide and both books through the old and new plugin gives the same HTML
  apart from the attributes listed below. The state machine loses about 300
  lines.
- New on these wrappers: `data-source-range`, `data-label="…"` on a labelled
  `@block`, and `data-sidebar="inset"` when written `@sidebar inset`.
- `@sidebar inset` works beside `@sidebar .inset`. `@block panel|slate|shard|codex`
  works beside `@block .dc-panel` (the `.dc-*` class form is unchanged).
- `@lede`, `@toc` and `@glossary` now accept extra classes and an `#id`,
  as the other wrappers always did.
- `@specialty-card`'s `data-position="odd|even"` now comes from a small core
  rule that numbers the cards in document order, as before.
- Snippets for `@sidebar-box`, `@glossary`, `@toc` and `@specialty-intro`.
  The `@block` snippet uses the variant word, and the chapter-start snippet
  opens its excerpt with `@fiction-excerpt`.
- **Nine section-styled components are declared as real core sections**
  (Gutterpress 0.11.16, `section: true`): `@column-panel`, `@tabbed`,
  `@card-grid`, `@citizen-walkthrough`, `@fiction-excerpt`, `@npc-stat`,
  `@flaws`, `@ideals` and `@dreams`, each with an `@end-…` closer and a
  snippet. `@npc-stat` is exactly `@section .dc-npc-stat`: same element, same
  classes, so every book that writes `@section .dc-…` renders as before.
  Modifier classes stay author classes (`@column-panel .gp-columns-2`). No
  variants: none of these is styled per specialty. The design guide uses the
  new markers; `components.yaml` lists them as plugin-origin, and its
  `card-variants` entry now describes `.section.dc-flaws` (the class the CSS
  actually selects).
- **`@specialty`, `@learning-path` and `@skill` are declared too, then
  transformed** ("declare, then transform"). Core now opens, nests and closes
  them, and two ordinary markdown-it core rules (`dcLearningPaths`,
  `dcSkillCards`, over a small inlined `forEachComponent` helper) rewrite what
  sits inside: the path's title, subtitle and sticker chain, `data-path-ref`,
  and one skill card per `####` heading. The state machine drops from 865 to
  468 lines (`plugin.js` is 97 lines shorter overall, new rules included):
  its skill, path and specialty flags and branches are gone. `@continue`
  inside a skill's card still opens the
  `{name} ▸` continuation card; the classifier that claims it ahead of core
  now reads core's marker tokens instead of the raw paragraphs.
- **`@card`, `@outcome` and `@procedure` are declared and transformed the same
  way.** Three more core rules (`dcCards`, `dcOutcomes`, `dcProcedures`) run
  ahead of the skill rules and rewrite what sits inside each. The state
  machine drops from 468 to 122 lines: it now holds only `@callout`,
  `@dm-note`, `@tape`, the retired `@roll-table` / `@options-table` no-ops and
  the image-only paragraph class. `plugin.js` is another 208 lines shorter
  (1,765 to 1,557), new rules, validation and docs comments included. The
  emitted HTML is unchanged: rendering the design guide and both books
  through the old and new plugin gives the same markup apart from the
  attributes and the one page listed below.
  - `@card` is `div.dc-card` with its heading, pull quote, body and footer as
    before, and takes classes, `#id` and `key=value` as before.
  - `@outcome` is `div.dc-outcomes`; `flush` is now a declared variant (it
    adds `.dc-flush` and `data-outcome="flush"`), and `@outcome .dc-flush`
    works too. The compact form (rows with no blank lines) still works.
  - `@procedure` still renders only the `ol.dc-steps`: its declared wrapper is
    hidden, so no `div` appears in the HTML.
  - A `@card`, `@outcome` or `@procedure` inside a skill stays inside the
    skill's card, as before.
  - New on cards and outcomes: `data-source-range`, so the editor can map them.
- **More structure checks.** An `@outcome` line that is not `roll | name |
  text`, a table, list or heading inside an `@outcome` (they are left out), an
  `@outcome` with no rows, and a `@procedure` with no numbered list are
  reported in plain words, at the line.
- `@specialty augmerc` is the new spelling for a specialty (names:
  `augmerc`, `proxy`, `streetwarden`, `gutterdruid`, `cybersurgeon`,
  `wirephreak`, `technosorcerer`, `etherlock`, `dualist`, `generalist`, each
  styled by `.dc-specialty.<name>`). `@specialty .augmerc` and
  `@specialty {.augmerc}` work unchanged and give the same element.
  `data-path-ref` reads the enclosing specialty's variant or class, so
  `@specialty .augmerc` still gives `AUG1`.
- **Structure checks, in plain words.** Skills sitting directly in a
  `@specialty` are reported once per run, at the first one ("This skill (and
  any right after it) is outside a learning path…"), and so
  is a `@learning-path` or `@specialty` that starts inside a skill. The usual
  cause is an `@end-learning-path` above the skills it was meant to close.
- Snippets: `specialty` shows the whole specialty > learning path > skill
  hierarchy, and `learning-path` shows its skills.
- **`@callout` and `@dm-note` are declared, and the state machine is gone.**
  `@callout` is a declared wrapper (`div.dc-alert` + the variant's class,
  author classes and `label="…"` as before) and `@dm-note` is its alias with
  the `dm` variant preset, so `@dm-note` is `@callout dm` and `@end-dm-note`
  still closes it. One small core rule (`dcCallouts`) adds the variant's
  default label ("Note", "Warning", "Dream Master Note", "Vibe", "Origin",
  "Visit", "Gear") when there is no `label="…"`; an explicit label wins. A
  missing or unrecognised variant is a plain note, as before. With `@tape`
  and the retired `@roll-table` / `@options-table` stripper gone too,
  `dimm_city_transform` and its `closeAll()` are deleted. What is left are
  four small core rules: the `@continue` bridge into skill cards, `> [!TYPE]`
  alerts, `ROLL THE DIE!`, and the image-only paragraph class (now
  `dcImageParagraphs`). `plugin.js` goes from 1,557 to 1,381 lines.
  The emitted callout is the same element, classes and label span as before.
  Core adds `data-callout="<variant>"` (and `data-label` when labelled) and
  `data-source-range`, and writes no newline between the wrapper and its label.
- `docs/adding-macros.md` and `docs/macros.md` now describe a plugin with no
  hand-written markers: the "hand-written marker" recipe is gone.
- devDependency `gutterpress` is `0.11.16`.
- `docs/plans/specialty-section-variants.md`: the plan for styling section
  components per specialty (`@npc-stat wirephreak`), for a later release.

### Removed

- **`@callout variant=…` is gone**, with no compatibility mapping: the variant
  is a bare word (`@callout note`, `@callout vibe`, `@callout .float-right
  origin label="…"`). Core reads `variant=origin` as a plain attribute, so the
  callout would render as a note; instead every `@callout` or `@dm-note`
  written that way gets one Problems message on its line: `@callout: no longer
  takes variant=origin; write "@callout origin" instead.` Edit the books:
  `variant=note` to `note`, `variant="vibe"` to `vibe`, `variant=origin` or
  `variant="origin"` to `origin`.
- **`@tape` is removed.** The marker was one line with no body and no
  `@end-tape`, which a declared marker cannot express yet: a `selfClosing`
  marker feature was requested upstream as gutterpress#344, and `@tape` can
  return as a declared marker once it exists. Until then write the raw
  `<div class="dc-tape">Label</div>` (`dc-flush` to run edge to edge), which
  renders the same HTML; the `.dc-tape` CSS stays. The design guide's
  examples use the raw form. A leftover `@tape label="…"` line now prints as
  the text it is.
- **The `@roll-table` / `@options-table` no-op handling** (deprecated in
  17.3.0), its `roll-table` entry in `components.yaml` and the design guide's
  note. Neither is a marker any more, so a stray one prints as text.
- `@block variant=panel`. No book or guide page used it; write `@block panel`.
- `@end-skills` (no book used it; it is plain text now).
- `@end-skill` no longer closes the `@learning-path` around the skill. It
  closes the skill, like every declared closer; `@end-learning-path` ends the
  path.

### Behaviour notes

- Declared wrappers nest as a stack and close at the next `@page`,
  `@section` or `@chapter`, or at the end of the file. A hand-written marker
  (`@learning-path`, `@callout`, …) no longer closes a wrapper that is still
  open. No book relied on that.
- A wrapper's `key=value` attribute is always `data-key` now: `lang=en` is
  `data-lang`, where the old code emitted `lang` (likewise `dir`, `role`,
  `tabindex` and `aria-*`).
- `@end-<wrapper>` with no open wrapper now warns
  (`declared_marker_close_without_open`) instead of being ignored. That now
  includes a stray `@end-skill`, `@end-learning-path` and `@end-specialty`.
- Specialties, paths and skills close like every declared marker: a new one
  of the same kind closes the previous and what is inside it, `@end-<name>`
  closes it and what is inside it, and `@page`, `@section`, `@chapter` and
  `@continue` close all of them. A `@page` written inside a specialty used to
  leave the specialty open across the page; it now ends the specialty. Use
  `@page-break` to break a page inside one.
- A `@skill` glued to the line above it (no blank line) is now a marker, as
  every declared marker is; it used to print as the text "@skill".
- A skill inside a learning path is numbered `PATHREF.N` by its place in the
  path. An `@end-skill` in the middle of a path used to end the path (the
  skills after it lost their tier); the path now stays open.
- A closer straight under a list item or a quote is a closer now, because core
  reads declared markers there: `@end-procedure` under the last step and
  `@end-card` under the footer quote no longer need a blank line (they used to
  be folded into the item or the quote and never closed).
- `@procedure` and `@outcome` left open at the end of a file warn with core's
  `declared_marker_eof_close` ("An open @procedure reached end-of-document…"),
  replacing the plugin's `unclosed_procedure`. An unclosed `@outcome` used to
  swallow the rest of the file without a word. `@card` still closes silently.
- `@end-card`, `@end-outcome` and `@end-procedure` with nothing open now warn
  (`declared_marker_close_without_open`) instead of being ignored.
- `@callout` and `@dm-note` nest like every declared marker: a new one closes
  the one still open (with what is inside it), `@end-callout` and
  `@end-dm-note` close it, and `@page`, `@section`, `@chapter` and `@continue`
  close it (a callout left open at a `@page` used to run on, and the next
  page's `<div>` ended up inside it). `@callout`, `@procedure`, `@end-procedure`, `@end-callout` is a
  callout with the procedure in it. One book chapter wrote exactly that; it
  used to close the callout at the `@procedure` and leave the steps and the
  closing paragraph outside its box, and now renders them inside it, as
  written.
- A callout written in a skill (even after its card, with no `@end-skill`)
  stays in the skill's card, as before. A stray `@end-callout` or
  `@end-dm-note` warns (`declared_marker_close_without_open`) instead of being
  ignored, and a bare word that is not a variant (`@callout vibes`) is a note
  with core's `unknown_variant` warning.
- `@dm-note` now takes author classes and an `#id` like `@callout` (it used to
  ignore them).
- A callout or `@dm-note` glued to the line above it (no blank line) is now a
  marker, as every declared marker is; it used to be folded into the
  paragraph.
- A bare word after `@card`, `@outcome` or `@procedure` is no longer a class
  (core reads it as a variant, and only `flush` is one): write `@card .wide`.
  No book or guide page used one.
- An `@outcome` shows only the lines of its own paragraphs: a list or heading
  inside it is no longer read as a row (it is reported instead).
- Core drops a declared marker that is already open and nests the next one, so
  a book that closes a path early (`@end-learning-path` above its skills) now
  has its next `@learning-path` nested in the last skill. The checks above name
  each place; remove the early `@end-learning-path`.

## [1.1.5] - 2026-10-09

### Changed

- **The chapter-opener chevron rules move from `chrome.css` into the
  chapter-opener template in `page-templates.css`.** No component sheet
  selects `.chapter`/`.page` any more, and the integrity test enforces
  that with no exceptions. Pixel-identical in both books.
- `docs/cleanup-backlog.md` gains a "Still considering" section:
  - the Field Guide's sidebar areas, with the inset-rail rules;
  - the specialty-card redesign;
  - the configurable chapter prefix;
  - the offset tokens.
- `docs/css-roadmap.md` records the warnings that are known and accepted:
  - the design guide's 8 heading jumps inside component examples, which
    need an `h4`;
  - the `clip-path` and `page-containment` lint false positives, reported
    as dimm-city/gutterpress#339.

## [1.1.4] - 2026-10-09

### Changed

- **The columns contract is refined.** Page and section column layouts
  stay in `page-templates.css`. A component may lay out its own insides in
  columns in its own sheet, on a selector rooted in its `.dc-*` class (the
  two-column skill cards, the card grid). The integrity test enforces that
  rule in place of an exception list. No CSS moved.
- The integrity test's remaining exceptions are genuine hooks: the outcome
  tiers, the chapter classes gutterpress adds itself, and the design
  guide's page labels.
- `docs/css-roadmap.md` records what the CSS review left to do, and in
  which order.

### Removed

- Two unused design-guide classes: `dg-face-sample` and the
  `dc-banner-demo` section class.

## [1.1.3] - 2026-10-09

### Removed

- Distance tags: the plugin no longer turns a `Distance` table inside a skill
  into pills (`buildDistanceTags`); it now renders as a plain table. Also
  removed `.dc-distance-tags`, `.dc-dist-tag`, `.dc-dist-ap`, `.dc-dist-name`
  and the `--dc-dist-*` tokens. No book had such a table.
- Unused combinations: `.dc-flush` on `.dc-intro`, `.dc-sub-header` and
  `.dc-steps`; `.dc-intro + .dc-alert`; `.dc-card-grid > h1/h2/.dc-intro`
  (put headings and ledes outside the grid); `.section > h2.dc-h3:not(:first-child)`;
  `.dc-toc ol > li > strong`.

## [1.1.2] - 2026-10-08

**Notes for books upgrading from 1.1.1:**

- Build on gutterpress 0.11.15 or later and drop `@page .dc-printer-page`
  and your own `print.signature`: the `dtrpg` preset now does both.
- Field Guide classes that moved into the package: `.fg-snug` becomes
  `.dc-snug`, and the book-wide two-column skill cards become
  `.dc-cards-two-col` on the specialty markers.
- Section panels, padding and splitting are tokens now. A book that
  restyled `.section` chrome by overriding properties should set the
  tokens instead (see the palette reference's Section table).

### Added

- **`.dc-cards-two-col`**: on any ancestor (`@specialty`, `@chapter`,
  `@page`, `@section`), every skill card inside gets a two-column body.
  This is the Field Guide's book-wide form as an opt-in. A card's own
  `.dc-two-col`, or `.dc-allow-split`, keeps its own form.
- **`.dc-snug`**: tighter paragraph and list-item spacing on a section or
  page, for one that would otherwise overflow by a line or two (from the
  Field Guide's `.fg-snug`).
- **Split skill cards keep their lead-ins with what follows.**
  `.dc-specialty .dc-skill-card.dc-allow-split` keeps its tab, first
  blocks and lead-in paragraphs with the next block (from the Field
  Guide's own sheet).
- **Section tokens.** A section's panel, shadow and padding now come from
  tokens (`--dc-section-surface`, `--dc-section-shadow`,
  `--dc-section-pad-*`), as does whether a box may split
  (`--dc-section-break-inside`, `--dc-alert-break-inside`). Variants and
  page templates set tokens instead of cancelling properties.
- **`test/integrity.test.js`**, which checks that:
  - every class the books use is styled;
  - every token that is read, or that the palette reference documents,
    is declared;
  - each stylesheet keeps its stated contract.

### Changed

- **Tested against gutterpress 0.11.15** (stable; was 0.11.15-alpha.1).
- **CSS quick wins from an architecture review.**
  - New tokens: `--shadow-ink` (the opaque wall-shadow colour, written
    out five times before) and four exact-value `--tint-*` mix sources
    for the literal `rgb()` colours inside `color-mix()`.
  - `--dc-section-tab-overlap` and `--dc-section-tab-indent` are now
    public `:root` tokens.
  - The TOC/credits masthead `h1` is now one rule instead of two.
  - Dead declarations are gone: the `--shadow-poster` layer a specialty
    card's own `clip-path` clipped away, `page-break-inside`, an empty
    rule, a no-op height reset, three `opacity: 1`, and the
    `break-before: always` Chromium ignores on learning paths.
  - `dc-native.css` loses its tombstones and is renumbered §1–8.
  - Pixel-identical in both books, except the even specialty cards,
    whose left border is now `1.5pt` like the rest (was `1.5px`).

- **Section styling is opt-in per variant, not cancelled by a central list.**
  - `.dc-plain`, `.dc-tabbed`, `.dc-column-panel` and `.dc-card-grid` set
    the section tokens.
  - The header bar's negative margins are derived from the padding.
  - The shared page templates (intro, credits, chapter opener) own their
    styling in `page-templates.css`; the chapter opener moves there from
    `section.css`.
  - Pixel-identical in both books.
- **The credits colophon shows its 4px front-matter rail again.** A rule in
  `dc-native.css` had overridden it. This is the one visible change, on
  each book's credits page.
- **Box splitting is decided in one place.**
  - Multi-column runs and `.dc-allow-split` set the break-inside tokens.
  - This replaces an avoid → auto → avoid override chain.

### Removed

- **`.dc-printer-page` and its `@page printer-blank`** (deprecated in
  1.1.1). gutterpress 0.11.15's `dtrpg` preset pads the interior to the
  4-page signature and reserves the blank last page itself, so a book
  needs neither the marker nor its own `print.signature`. The Field
  Guide, built on 0.11.15 without either, keeps its 232 pages
  pixel-identical and still ends on four blank pages.
- `--shadow-tint`, and `.dc-roll-the-die`'s `box-shadow: var(--shadow-tint)`:
  a bare colour is not a valid shadow, so it never rendered.
- `.dc-suppress-footer` and its `@page clean` (and the design guide's
  mirror of it): no book used footer suppression.
- The design guide's dual specialist and generalist skill-tree specimens
  (Variant Gallery; The Specialty System's "One source" section, now
  "eight shapes"). Those two specialties take their skills from the other
  eight and have no trees of their own, so the specimens printed a
  generic `PATH1` sticker for something that cannot exist.

### Fixed

- The catalog's glossary entries: a glossary item is a plain paragraph
  inside `@glossary`, and no doc or gallery page writes `.dc-terms-item`
  any more, so `glossary-item-authored` is retired.

## [1.1.1] - 2026-10-08

**Notes for books upgrading from 1.1.0:**

- A learning-path banner is now an `h3` (was `h2`), and a skill's title an
  `h4` (was a `span`). A book stylesheet that targets `h2.dc-spray` or
  `span.dc-tab-title` needs the new tag.
- Unused components were removed; check `docs/cleanup-backlog.md` and the
  Removed list below before relying on any of them.
- Tested against gutterpress 0.11.15-alpha.1, whose `dtrpg` preset now
  does the DriveThruRPG blank last page and K-only black text.

### Added

- **Heading look classes `.dc-h3`–`.dc-h6`.** A heading keeps its outline
  level and takes another level's look (`## Useful Items {.dc-h3}`), so a
  book can stop skipping levels to get a smaller label: gutterpress flags
  every skip. The section header bar and the in-section accent rule follow
  the class, not the tag. On a paragraph, the class sets a line in
  heading type outside the outline. The Field Guide's 13 skipped levels
  are fixed this way and render pixel-identical. Documented in the
  design guide's Typography chapter (Level and look).

### Changed

- **Tested against gutterpress 0.11.15-alpha.1** (devDependency, was
  0.11.13), the release that upstreams this package's two DriveThruRPG
  workarounds: `preset: dtrpg` now pads to a 4-page signature and always
  ends on a blank reserved page (`print.reserveLastPage`,
  dimm-city/gutterpress#332), and prints near-black text on the black plate
  only in PDF/X builds (`pdfx.blackText: k-only`, dimm-city/gutterpress#331).
  Verified on the Field Guide with the alpha: its 228 content pages render
  pixel-identical to 0.11.13, and without any workaround the book ends on
  4 pure-white pages (232). The design guide's Publishing chapter documents
  both settings.
- **Specialty chapters nest in the outline.** A learning path's title was
  emitted as an `h2`, the same level as the specialty name, and a skill's
  title as a plain `span`, so the app's contents panel and the PDF
  bookmarks listed every skill tree beside its specialty and no skills at
  all. The plugin now emits the heading levels the markdown is written
  at: specialty (`##`) > learning path (`h3.dc-spray`) > skill
  (`h4.dc-tab-title`). The CSS follows, and both books render
  pixel-identical. A stylesheet that targeted `h2.dc-spray` or
  `span.dc-tab-title` needs the new tag. A real space
  (`span.dc-path-sep`, carrying the 10px gap the sticker's margin used to
  give) separates a banner's tree code from its title, so the outline
  reads "PRX1 Refuse Finality", not "PRX1Refuse Finality".

### Fixed

- **DriveThruRPG PDF/X builds keep live text.** The brick wall was an RGBA
  tile blended with `background-blend-mode: multiply`, so every walled page
  carried transparency, which PDF/X-1a cannot represent: Ghostscript
  flattened each one to a raster image — no live text or embedded fonts
  (a one-page book failed validation outright), and black text left
  four-colour, because `pdfx.blackText: k-only` only reaches vector text.
  The wall is now `images/brick-wall.png`, the same tile multiplied into
  `--bg` and flattened to an opaque image, painted with no blend mode:
  it renders the same (design guide wall pages differ by 0.15/255 on
  average), and with gutterpress 0.11.15-alpha.1 a DriveThruRPG build's
  body text now prints on the black plate only (separations: C = M = Y = 0
  under every glyph). A book that retints `--bg` no longer tints the
  brick; see the note in `dc-native.css` for baking a tile.
- **Nothing in the package paints transparent.** The 25 other uses of
  transparency — semi-transparent shadows, tinted fills, `opacity` on
  stickers, rules, the tape dashes and the pull-quote mark — each flattened
  their page in PDF/X-1a just as the wall did. Each is now pre-composited
  with `color-mix()` onto the surface it sits on, so it prints the same
  colour, opaque. Shadows on the wall mix against the new `--wall-tone`
  (`#c1beb8`, the tile's measured mean). Measured on both books: layout and
  page counts unchanged, and no page changes more than 0.7% of its pixels.
  The AP chip loses its soft 6px blurred shadow, which has no opaque form,
  and keeps its hard one. Every change, with where to look, is in
  `docs/print-transparency-inventory.md`. A new convention test fails on
  any transparency in the stylesheets, with no exemptions (the one
  translucent holdout, the unused cover-page composite, was removed).

- **No stray ink line across the folio row.** A skill card, learning-path
  banner or specialty intro that opened a page printed the top 2–4px of its
  outline at the foot of the PREVIOUS page: a full-width black (or accent)
  line between the folio and chapter chips. The outlines reached above
  their component's box (`top: -4px`, `translateY(-2px)`), and Chromium
  fragments that part onto the page before. Each outline now sits inside
  its own box: the card starts 4px higher and pads its tab 4px down
  (`padding-top: 4px; margin-top: -4px`), the banner 2px likewise, and
  the intro pads its content 2px. Mid-page nothing moves; a component that
  opens a page sits 2–4px lower. Measured: the line is gone from all 17 Field Guide pages and
  the 1 design guide page that had it; page counts are unchanged (232, 132) and
  no text changes page. (It became visible with 1.1.0's DriveThruRPG
  margins, which moved the page breaks; the cause dates from 1.0.0.)

- **Accent rails print as vectors in PDF/X.** The 3–5px coloured rail down
  the left of sections, ledes, path banners, the Panel and Shard blocks,
  and the front-matter and intro panels was a hard-stop
  `linear-gradient`. The PDF/X conversion turned each gradient into a
  45 ppi bitmap, so the rail's edge printed soft, and
  `gutterpress preflight` flagged the pages as low-resolution. Each rail
  is now an inset `box-shadow` over a flat fill: it looks the same and
  prints as a vector.
- **Design guide: preflight checks the right page size.** Its manifest
  declared 612 × 792 pt (the bare Letter trim), so `gutterpress preflight`
  failed every build on page size. It now declares the sheet the CSS
  prints: 621 × 810 pt, the trim plus DriveThruRPG's bleed.

- **`.gp-columns-flow` works.** Core declares it in its own layer, which
  this package's `column-fill: balance` on every `.gp-columns-2/-3`
  outranked, so a run marked to flow stayed balanced. The balance rule now
  skips runs marked `.gp-columns-flow`.

- **Catalog statuses.** `plain`, `img-float`, `full-page` and
  `printer-page` were marked `unused` although a book uses each: the
  design guide renders the first two, SysOps uses `full-page`, and the
  Field Guide still ends on `@page .dc-printer-page` until it builds on a
  stable gutterpress 0.11.15. They are `live` now.
### Removed

- `images/brick-bg-01.png`, the RGBA wall tile, is no longer published
  (it now lives in the repository's `source-art/`). Neither Dimm City book
  referenced it; a book that did should use `images/brick-wall.png`.
- **Dead styling, from an orphan audit of the package, the design guide and
  the Field Guide.** Each item was used by no book (Field Guide, Design
  Guide, SysOps), and both books render pixel-identical without it:
  - components: the cover-page composite (`.dc-cover-*`, with
    `--dc-cover-meta-border`), the contents-page rows (`.dc-toc-row/-no/
    -title/-page`), `.dc-portrait` (with `--dc-portrait-*`), the roll badges
    `.dc-roll-lucid/-surreal` (with their colour tokens), `.dc-path-subtitle`,
    the glossary item `.dc-terms .dc-item` (with `--card-border-color`),
    `.dc-dashed-rule`, `.dc-tape.dc-margin-sm`, `.dc-sidebar-box-divider`,
    `.dc-outcome-table` and `.dc-callout`. Their catalog entries are now
    `retired`.
  - rules for markup the plugin no longer produces: `.dc-sticker.active`,
    the `ol`/`li` rules under `.dc-ability` (abilities are no longer
    lists), and `h5` and `ol > li` inside a two-column skill card (both
    are converted before they get there).
  - stale comments naming deleted files or classes (`dc-tokens-print.css`,
    `components.css`, `tokens.css`, the `.pmd-*` utilities, `.dc-accent-X`,
    old design-guide chapter names, undeclared tokens).
  Styling the audit found unused but still reachable is listed in
  `docs/cleanup-backlog.md` for review.

### Deprecated

- **`@page .dc-printer-page`.** gutterpress 0.11.15+ reserves the blank
  last page in core. The class still works — a book that keeps it gets one
  printer page plus padding, still ending blank — and goes in the next
  major.

## [1.1.0] - 2026-10-07

**Layout note for books upgrading from 1.0.x:** the page margins now follow
DriveThruRPG's print specification (text at least 0.5in inside the trim),
which takes 0.25in off every page and reflows the whole book. Build and
review your book after upgrading; the Field Guide needed a short layout
pass (see `dc-op-manual`, branch `design/plugin-updates`). DriveThruRPG
books should also end with `@page .dc-printer-page` and set
`print: signature: 4` in `manifest.yaml`.

### Added

- **`@page .dc-printer-page`**, a completely blank last page (no wall, no
  footer). DriveThruRPG reserves a book's final page for printer
  information: the interior must be one page short of its signature (4 for
  US Letter) or end on a blank page. End the last chapter with this marker
  and set `print: signature: 4` in the manifest — gutterpress pads with
  blank pages to the next multiple of 4 — and the book always ends blank.
  Verified in the Field Guide (228 content pages + 4 blank = 232).
- **Variant Gallery** (design guide chapter 11): every element with more than
  one variant, its variants on one stage — all ten skill trees (each
  specialty's first learning path with one skill card, Field Guide content
  excerpted), the skill-card switches (tier override, both highlight forms,
  two columns, outcome table), every AP chip, the ten specialty intros and
  cards, class tags, alerts, blocks, choice cards, and the flush, heading,
  section, sidebar and image-float variants.
- **The design guide lives here.** `design-guide/` is the Dimm City Design
  Guide book, moved from `dimm-city/dc-op-manual`. Its manifest loads the
  package from this checkout (`extensions: - ../`), so it documents and
  renders the working copy: `npm run dev` previews it, `npm run build`
  renders the PDF, and the test suite uses it as the fixture
  (`test/design-guide.test.js`: every chapter renders clean, every macro and
  alert type is demonstrated, and each chapter's HTML is snapshotted under
  `test/__snapshots__/`). CI builds the PDF with the PR's plugin and CSS and
  uploads it; the release workflow attaches it to the GitHub release; a
  *Publish design guide* workflow deploys the HTML build to GitHub Pages.
- **`@glossary` is demonstrated** in the component gallery, which used raw
  HTML for the term-list specimen before.

### Changed

- **Page margins follow DriveThruRPG's print specification.** Its
  [Quick Specifications for Print Books](https://help.drivethrupartners.com/hc/en-us/articles/12780800178583-Quick-Specifications-for-Print-Books)
  require all text at least 0.5in inside the trim. The bleed (0.125in on
  the three outside edges, none at the spine) and the outside and binding
  margins already complied; the top did not (0.375in from the trim) and
  neither did the footer chips (0.43in). Top margin 0.5in → 0.625in on the
  sheet (0.5in from the trim); bottom 0.75in → 0.875in, as the new
  `--bottom-margin` token, so the chips print 0.55in from the trim. The
  "Citizen File" running head, which printed 0.1in from the trim, sits at
  the foot of a 0.875in top margin. Footer chips re-homed by a `.gp-flush`
  pin are top-aligned like native ones (gutterpress centres them, which put
  them 0.24in from the trim). A card title too long for its card breaks
  rather than running into the margin. **This reflows every book:** the
  Field Guide goes from 221 to 238 pages and now has no text inside 0.5in
  of the trim (it had 1,273 words on 204 pages); the design guide goes from
  126 to 131.
- **Design guide: explainer pages print plain, specimens sit on the wall.**
  Part 1 pages (and the Part 2 overview) are `@page .dg-doc`, a named page
  with a white background and neutral headings, tables and contents, so guide
  text can't be mistaken for a component. Each rendered result is wrapped in
  a framed `.dg-stage` that carries the brick wall; whole-page specimens and
  the Part 2 example pages keep the full brick page. Chapter ledes, the
  contents lists, and the explainer notes and column panels that used
  package components are now plain guide markup. All of this lives in
  `design-guide/` (markdown and `styles/guide.css`); the package is unchanged.
- **Design guide: print-design review pass.** Readability and finish fixes
  from a review against the print-quality rubrics, all in `design-guide/`:
  - Code boxes are set in IBM Plex Mono (OFL, bundled in
    `design-guide/fonts/ibm-plex-mono/`), 9pt on 1.4 leading, without the
    doubled blank lines; fences of 20+ lines may split across pages.
  - Guide text is capped at a 5.1in measure (about 65–70 characters) on 1.4
    leading; tables are 10pt and may run across pages.
  - Chapters open with a "Chapter N" label; H1 26pt, H3 13pt. Doc pages
    carry a plain running foot (folio and chapter title); the contents list
    has page numbers; Part 2 has a title page and E.1–E.6 chapter badges.
  - YOU WRITE / RESULT labels are 8pt; YOU WRITE is cream on blood (7.7:1).
  - Specimen stages stay whole unless marked `dg-tall`; prose specimens sit
    on paper (`dg-on-paper`); two Do/Don't pairs (flavor in bold italic,
    body text on bare wall).
  - Typeface specimens for lixdu, Titillium Web and Tomorrow; palette
    swatches are 1in and each carries a CMYK build from the CGATS21_CRPC1
    profile (the hand-entered four-row CMYK table is replaced).
  - Fixed: the type-scale table listed H1–H4 at stale sizes; the guide's
    inline-code style leaked into the Part 2 examples (invisible text on a
    dark callout), and its `hr` rule replaced the package's dashed rule in
    the specimen; the inset-sidebar and art-plate specimens no longer leave
    a RESULT tab stranded at a page foot.
- **Tests run against gutterpress 0.11.13** (devDependency, was 0.10.11).
- **`test/fixtures/all-macros.md` and its snapshot are gone**; the design
  guide is the fixture. `npm run test:update-snapshot` is now bun's own
  `--update-snapshots`; `scripts/update-snapshot.mjs` is removed.

### Fixed

- **No blank page after a two-column page that ends in a spanner.** A
  `@page .gp-columns-2` page ending in a full-width section printed an
  extra blank page under the DriveThruRPG margins (Field Guide: Quickstart
  vs. Deep Dive): the section's bottom margin pushed the page box past its
  one-sheet minimum. A multicol page's last child has no bottom margin.
  Design guide unchanged; Field Guide loses the blank page.
- **The introduction page keeps the normal margins.** `.page-intro` shared
  the `front-matter` named page with the Contents and Credits, whose side
  and bottom margins are zeroed for their full-bleed masthead — so the
  intro's chevron, lede and section sat flush on the sheet edge. It has its
  own named page now, `front-matter-intro`: default margins, no footers.
  The Field Guide writes its introduction as a plain `@page` and is
  unaffected.
- **No more pages printed as images.** `filter: drop-shadow()` on the
  intro page and on the labelled chapter-opener page made Chromium print
  each of those pages as one 300ppi bitmap with a soft mask: no live text,
  and a transparency mask PDF/X-1a forbids. Both shadows are vector now
  (box-shadow on the lede, section and opener badge; the opener section's
  own clipped `::after`). Design guide: 8 pages regain live text. The
  Field Guide uses neither and is unaffected.
- **No hairline across the page after the credits.** The colophon fills to
  the sheet's bottom edge, so its poster shadow's 3pt drop overflowed the
  sheet and printed as a line across the top of the next page — over the
  Field Guide's Contents masthead. The colophon keeps the shadow's side
  offset and drops the downward one. (Clipping the page was rejected: it
  would also clip a pinned or bleed plate.) Field Guide: p.2 loses the
  line, and p.1 shows the colophon's side shadow starting level with its
  top; nothing else changes.
- **Specialty art plates print full bleed.** The `.page` overflow guard
  (page-templates.css) exempted pages holding `.gp-bleed`/`.gp-pin` art but
  not `.dc-specialty-art` or `.dc-full-page`, so a plate on a page with no
  other pinned art was cut at the text column — a 100pt strip of bare wall
  down its outside edge (design guide p.45, p.105). The Field Guide's
  plates were full width only because its specialty pages also carry
  pinned art. Field Guide unchanged.
- **A long standalone banner title keeps its skew tab inside the margin.**
  `.dc-spray`'s `::before` tab overhangs its right edge by 18px; a title
  that filled its column pushed the tab past the margin, which is print
  shrink-to-fit for the whole book once the page does not clip (found by
  the build's width audit after the plate fix). Standalone banners cap at
  the column less the tab; learning-path banners, which span their shell
  with the tab pulled inside, are exempt. Field Guide unchanged.
- **A learning-path banner stays with its first card.** The shell is never
  split and keeps with the next card, and the first path after a
  specialty's art page drops its 8px top margin — moved into the package
  from the Field Guide's own sheet, which measured both. Without them the
  design guide printed the Biting Distance banner alone, with the edge of
  the first card's tab at the page foot. The package's `break-before:
  always` on `.dc-learning-path` is not a value Chromium supports and does
  nothing; it is left as is (making it valid would put every path on a new
  page). Field Guide unchanged.
- **A credits page that overflows no longer prints under the next page.**
  `.page.page-credits` had an exact one-sheet `height`; when its colophon
  did not fit, the colophon moved to a second sheet but the page box stayed
  one sheet tall, so the following page started on that same sheet and was
  painted over it (design guide: the Introduction over the colophon). It is
  a `min-height` now: a page that fits is still exactly one sheet, so the
  pinned plate still seats on the sheet edge, and the Field Guide renders
  pixel-identical. The design guide's credits example also pins its plate
  like the Field Guide's (`.gp-pin .gp-bottom .gp-full`) instead of placing
  it in the colophon, which is what had made it overflow.
- **Variable AP chips print as variable.** The plugin emitted
  `.dc-ap.variable` but the CSS only styled `.dc-ap.var`, and a `VAR AP`
  cost got no variable class at all. Both spellings are styled now, and
  `VAR` is detected alongside ranges and `X`. Visible change in the Field
  Guide: 13 pages, each a range-cost chip (`2-X AP` and the like) turning
  from standard blue to variable magenta; no layout change.
- **Short two-column runs no longer print full-page height.** `dc-native.css`
  §10b set `column-fill: auto` on every `.gp-columns-*` run; with no fixed
  height that fills the first column to the page foot, so a short column
  panel became a full-height box with an empty right column, and a heading
  above one was stranded alone when the box could not fit under it. The
  rule is `balance` again, and the two per-shape `balance` exceptions it
  made redundant are removed. A run that needs sequential fill opts in with
  core's `.gp-columns-flow`. The Field Guide's 221 pages render
  pixel-identical before and after.
- **A lede never splits** (`.dc-intro { break-inside: avoid }`), and the
  section after a lede may start a new page. Core glues every section to
  what precedes it, which chained heading → lede → section; when the section
  could not fit, the lede split and painted an empty panel to the page foot.
- **`@sidebar .inset` with a single paragraph** set that paragraph in
  centred display caps: the rail's closing-line rule matched it as the last
  child. It now applies only from the second paragraph on. The inset rail
  also keeps the sidebar's paper surface instead of a transparent one that
  put its text on the brick wall.
- Two design guide chapters (`303`, `306`) closed `@procedure` on the line
  right after a list item, which markdown folds into that item, so the
  marker never closed and the chapter rendered with a layout warning.

## [1.0.1] - 2026-09-25

### Changed

- **The layer statement drops `book`**: `dc-fonts.css` now declares `@layer
  dc.tokens, dc.base, dc.components, dc.templates, dc.pages;`. Gutterpress
  0.11.0 wraps every extension's CSS in its own cascade layer (`@layer
  ext.gp-dimm-city` for this package), so the package's own `dc.*` layers are
  now sublayers nested inside that wrapper rather than top-level layers, and
  a `book` sublayer declared here would only be reachable from inside this
  package — a consuming book's separate `styles:` sheet can't nest into it.
  Nothing in this package or any known consuming book ever put rules inside
  `@layer book`, so there is no rendered change.

### Docs

- **README quick start now requires Gutterpress 0.11.0+** and drops the
  `gutterpress ext remove ./extensions/clean-book` workaround: Gutterpress
  now layers every extension's CSS itself (in `extensions:` list order), so
  this package's rules can no longer be jumped by an unlayered starter look,
  and `gutterpress new` no longer scaffolds one anyway. The "Your own CSS"
  section no longer recommends wrapping book overrides in `@layer book` —
  a book's own `styles:` sheets are unlayered by the engine and already beat
  this whole package at any specificity.

## [1.0.0] - 2026-09-25

First release as a standalone package. Extracted from the private
`dimm-city/dc-op-manual` repository, where it lived at `dc-design-guide/` as a
folder extension that the Dimm City books referenced by relative path. The
design guide *book* stays in that repository and now consumes this package
exactly like any other book.

### Added

- **Installable from npm.** `gutterpress ext add gp-dimm-city` vendors the
  package under a book's `plugins/npm/` and pins the exact version — no Node
  packages in the book repo. `"type": "module"` in `package.json`, which the
  old folder package lacked: Gutterpress's npm loader parses a `.js` entry as
  CommonJS without it and refuses the plugin.
- **The brick-wall tile ships.** `dc-native.css` paints the page background
  from `images/brick-bg-01.png`; the old package's `files` list never included
  it, so a published copy would have failed every build with a missing asset.
  `test/package.test.js` now follows every `url()` in every stylesheet into
  the tarball.
- **Font licences.** Titillium Web and Tomorrow ship with the OFL 1.1 text
  from their upstream repositories beside the files; Lixdu ships with its own
  licence file. Fonts are grouped per family under `fonts/` with readable
  names instead of export UUIDs (byte-identical; fonts inline at build time,
  so the rename cannot change a page).
- **Snippets** for the desktop app's snippet picker: every macro an author
  reaches for (`@skill`, `@learning-path`, `@specialty`, `@callout`, `@card`,
  `@gear`, `@block`, `@outcome`, alerts, …) and the three front-matter pages
  every Dimm City book writes (contents, credits, chapter start).
- **Tests** (`bun test`): a fixture snapshot of every macro's output, the
  behavioural tests carried over from the book repo, and package checks —
  every declared path and every stylesheet asset in the tarball, one licence
  per font directory, the cascade contract below, and no runtime imports.
- **CI and release workflows**: tests on every push and PR; a manual release
  workflow that bumps, tags, publishes to npm with provenance via OIDC
  trusted publishing, and cuts the GitHub release.

### Changed

- **`css/` is `styles/`**, matching Gutterpress's extension template. Same
  sixteen sheets in the same cascade order; `tokensFile` now points at
  `styles/dc-palette.css` (the brand palette) rather than the specialty
  identity tokens.
- **The layer statement is `@layer dc.tokens, dc.base, dc.components,
  dc.templates, dc.pages, book;`** — `dc.guide` is gone. A book's own sheets
  belong in `@layer book`, the last layer, which outranks every `dc.*` layer;
  a book that must beat the unlayered `dc-native.css` lists an unlayered sheet
  after the extension. (`dc.guide` existed for the design guide's own
  scaffolding; that book now uses `book` like everyone else.)
- **Front-matter chrome moved in from the books.** The contents-page rows,
  credits role labels and prose, and chapter-start heading rules that lived
  in the design guide's sheet (`dg-overrides.css`, layer `dc.guide`) and the
  credits-page flex layout from the field guide's native sheet are now in
  `page-templates.css` and `dc-native.css`: every Dimm City book writes these
  pages. Values are carried as rendered. Two rules that only ever lost to
  them by layer order were reconciled so nothing changes on the page: the
  dead magenta TOC-divider rule (`page-templates.css`) is removed, and the
  credits role-label colour now says `--ink`, which is what it always
  rendered.
- **Specialty break control moved in from the field guide**: `.dc-specialty
  .dc-learning-path { break-before: always }` and the `.dc-allow-split`
  escape, in `page-templates.css`.
- Plugin `metadata` no longer carries its own `version` (17.3.0 in the book
  repo); `package.json` is the only version. Its `name` is now "Dimm City".
- Stale comments across the stylesheets and plugin that named files from the
  book repo (`dc-components.css`, `native-furniture.css`, `dc-tokens.css`,
  `engineStyles`, `fg-overrides.css`, `dg-overrides.css`, `index.css`) now
  name the package's own files or "the book's own sheet".

### Removed

- `index.css` (an `@import` entry point that reached into the field guide's
  folder) and `dg-overrides.css` (design-guide-only scaffolding, now that
  book's own sheet) are not part of the package.
- The catalog entries `palette-swatch` and `table`, and the `ignore:` block —
  all design-guide-only.
- The `dimm-city-components` package name.
