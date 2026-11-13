@chapter #ch-templates .templates .dg-guide ch="8"

@page .dg-doc

Chapter 8 {.dg-kicker}

# Page Templates

A word on `@page` chooses a page's geometry --- margins, footers, running headers --- and `@section` variants build the recurring pages of a Dimm City book. Each template below is a skeleton to copy; the finished page is in Part 2. {.dg-lede}


## Page geometry

US Letter, perfect-bound, with bleed: the gutterpress `dtrpg` preset, declared in `manifest.yaml`. The geometry follows DriveThruRPG's published print specification ([Quick Specifications for Print Books](https://help.drivethrupartners.com/hc/en-us/articles/12780800178583-Quick-Specifications-for-Print-Books)): a 0.125 in bleed on the three outside edges and none on the binding edge; all text at least 0.5 in inside the trim; art that does not bleed at least 0.25 in from the outside edges and 0.5 in from the binding edge.

The `@page` rules in the package's `styles/page-rules.css` set the margins on the sheet, which includes the bleed, so each bleed-side margin is the trim distance plus 0.125 in.

| Dimension | On the sheet | From the trim | DriveThruRPG minimum for text |
|---|---|---|---|
| Sheet (trim + bleed) | 8.625 × 11.25 in | --- | --- |
| Trim | --- | 8.5 × 11 in | --- |
| Bleed | 0.125 in at top, bottom and the outside edge; none at the spine | --- | --- |
| Top margin | 0.625 in | 0.5 in | 0.5 in |
| Bottom margin (the folio and chapter chips sit in it) | 0.95 in | 0.825 in | 0.5 in --- the chips sit at the top of the band and end 0.5 in from the trim; a sheet that fills a page ends 0.10 in above them |
| Outside margin | 0.625 in | 0.5 in | 0.5 in |
| Binding margin | 0.5 in | 0.5 in | 0.5 in |

A `citizen-file` page has a 0.875 in top margin. Margins swap per recto and verso: the binding margin is on the spine side. Extend any full-bleed image 0.125 in past the trim.

## Page words

| You write | Footers | Use for |
|---|---|---|
| `@page` | `p.N` and `c.N` in opposing corners, the chapter's name between | Every body page |
| `@page contents` | none | The contents page |
| `@page credits` | none | The credits page |
| `@page intro` | none | The introduction (a `@lede`, then a `@section flat`) |
| `@page chapter-start` | none | A chapter opener |
| `@page citizen-file` | `p.N`, `c.N` | A Citizen File walkthrough page, 0.875 in from the top |
| `@page specialty-catalog` | `p.N`, `c.N` | The specialty catalog: a two-page spread that opens on a left page |
| `@page wall-1` … `wall-13` | `p.N`, `c.N` | A wall instead of the brick (below) |
| `@page full-bleed` | none | Zero margins; full-bleed art (core's word; the raw `.dc-full-page` is styled the same) |
| `@page blank` | none | A deliberately blank page (core's word) |

The `c.N` footer is the chapter number from `@chapter ... ch="N"`. A chapter split across files repeats its `@chapter` line in each.

### The page chips

The folio and the chapter number print as stickers, never as bare type. The folio (`P.121`) is a paper-cream sticker with an ink edge and a hard shadow; the chapter chip (`C.N`, which a book can restate as `E.N` as this guide does for Part 2) is a stamped coupon: a solid face with cream type and the same edge and shadow. Both are 17 pt tall with 10 pt type centred in the face, and both sit 0.125 in below the text block, inside DriveThruRPG's 0.5 in text minimum, so a box that runs to the foot never touches them, on recto and verso, for every page word that prints them. The coupon is magenta by default; to colour it with a chapter, put the chapter's pages on a named page, `:where(#ch-rules) > .page { page: dc-chip-rust; }` (blue, rust, violet, amethyst or amber; the `specialty`, `rules` and `lore` chapter words do it for you). Name the page with the low-specificity `:where()` so a page's own template name still wins. A `citizen-file` page's running head is the same sticker in amber at the top.

### Stone walls

Six walls can stand in for the brick on any page, over the whole sheet: write the word on the page, or add its class beside another page word.

```markdown
@page wall-3

@page chapter-start .dc-page-wall-3

@specialty .augmerc .dc-page-wall-3
```

| Word | Wall |
|---|---|
| `wall-1` | Coursed rubble: rough stones in rough courses, grimy and damaged |
| `wall-2` | Ashlar: big dressed blocks, some double height, grimy and damaged |
| `wall-3` | Random rubble: big rounded stones, no courses, grimy and damaged |
| `wall-4` | Running bond: small bricks, half-lapped, grimy and damaged |
| `wall-5` | Flagstone: flat slabs bedded in rough courses, grimy and damaged |
| `wall-6` | Square setts: square blocks, half-lapped, grimy and damaged |
| `wall-7` | Rusted steel plate: riveted plates under rust, with bullet holes, torch cuts and claw marks |
| `wall-8` | Circuits set into the wall: a grey render with a few broken boards set into it |
| `wall-9` | Moss and fungus: coursed rubble under moss, lichen, bracket fungi and creepers |
| `wall-10` | Operating room: grimy clinical tiles with blood spatter, runs and filth |
| `wall-11` | Into the aether: stone and metal plates torn by rifts that pull the wall in |
| `wall-12` | A technosorcerer's lab: conduit, bulbs and LED strips, chalked circuit-sigils, shelves of jars and candles |
| `wall-13` | A bazaar: stalls under faded awnings, bulb strings, hanging goods, crates along the foot |

Walls 1 to 6 are the city's own stone: ash stone with grey joints, as dim, dirty, damp and dangerous as the brick, which is weathered the same way. Soot and dirt in the joints and run down the faces, damp streaks, wet patches and tide marks, mould and fungus, soot, scorches and grease stains, chips, cracks, bullet pocks, claw gouges torn into the stone, some fresh and some old, scratched tallies and glyphs, and specks and spatters of dried blood: grim, not gory. The heaviest marks are kept moderate where the text sits and some damage is left in the margins, so every page shows it and the white sheets on it still lead. Each repeats only every 12in or so, so a page never shows the same mark twice; all thirteen are drawn at 300 DPI, so they print sharp. Walls 7 to 13 are drawn, in their own colours, and repeat no sooner than a spread, which reads as one wall across the spine; everything on them already sits on its own paper, panel or chip, so nothing changes for the text. A specialty has no page of its own around it, so its wall class goes on `@specialty`: the class only names its pages, so nothing on them moves, and its art plate keeps its full-bleed page, on the same wall. The chapter chip keeps its colour on a wall page in a `specialty`, `rules` or `lore` chapter. In a chapter a book colours itself, wire the wall pages the same way as the chapter: `#ch-rules > .page.dc-page-wall-3 { page: dc-wall-3-rust; }`. A page word with chrome of its own (`contents`, `credits`, `intro`, `citizen-file`) keeps the brick, and a full-bleed plate never takes a wall.

### Where pages break

Pagination is part of the package, so every book gets it: text keeps three orphans and three widows in panels and callouts; a skill card splits between ability rows, never leaving one row on a page with a hand's breadth of empty cream under it; headings, tape dividers and stat-block names stay with what follows. A panel splits where the page ends; one that must be kept whole whatever it costs is `{.dc-avoid-split}`, and a book that wants all its short panels whole says so from its own sheet (`--dc-section-break-inside: avoid`), since what counts as short depends on its content.

### Text on the wall

Nothing is ever printed straight on the brick. Anything you write directly on a page with no `@section` or callout around it dresses itself:

| You write | It prints as |
|---|---|
| `# Title` | A banner in the chapter's accent colour with cream type |
| `## Heading` | A paper slip bolted to the wall: an accent rail on the left, a dashed ink foot, a hard shadow and a slotted bolt head in each top corner |
| `### Heading` | The same slip at the full width of its column, with a thinner rail and foot and no bolts |
| `#### Heading` and smaller | A label slip that shrinks to its words, framed in ink |
| `## 4. Heading` | A step: the slip, its number set as a chip in the chapter's colour, so a procedure's steps (the Citizen File's 0–7) read as one sequence |
| Paragraphs, lists, quotes | One paper sheet per run; the sheet ends where the run does. A list hangs its marker in a 1.1em indent (1.6em for numerals) inside the padding of the sheet, so wrapped lines align under the first word. A run of prose in `@columns` is one sheet and does not split across a page |

Every heading has the same small gap under it, whatever follows: a sheet of text, a panel, a callout, a card or a table. Headings that already carry a look (`{.dc-chevron}`, `{.dc-spray}`) and everything inside a section keep their own. The chapter word recolours the rail and the banner. To change the slip or sheet for a book, set `--dc-page-slip-bg`, `--dc-page-slip-ink`, `--dc-page-slip-edge`, `--dc-page-slip-shadow`, `--dc-page-slip-bolt`, `--dc-page-slip-bolt-face` and `--dc-page-slip-bolt-size` (the bolt heads on a `##` slip: ring and slot, face, diameter), `--dc-page-slip-gap` (the space above a slip), `--dc-page-slip-foot` (the space below it, 6pt), `--dc-page-sheet-pad` or `--dc-page-title-ink`. A plain heading that follows a box (a ladder, a stat grid, a table) takes `--dc-heading-gap` above it. Explainer pages like the one you are reading (`@page .dg-doc`) print plain on white and are not wall pages.


## Where the content sits

A location is the page template or the chapter a section sits in. It draws nothing: it sets tokens, and the components read them. That is how one `@section panel` looks right in an opener, in a rules chapter and in a lore chapter without a rule per book.

A **chapter word** sets the colour register of every panel in the chapter. It recolours a panel's accent and nothing else: an alert, a faction, a choice card or a gear entry keeps its own identity in every chapter, so a warning is a hazard sign and a Dream Master note is a file under an ink bar wherever they sit:

| You write | Section accent | Use for |
|---|---|---|
| `@chapter citizen-file` | magenta-deep | Who you dream to be |
| `@chapter specialty` | blue-dark | The specialty gateway |
| `@chapter rules` | rust | How to play |
| `@chapter dm` | ink | Behind the screen: the Dream Master's chapter |
| `@chapter gear` | amber | The armory: cybernetics, weapons, gear |
| `@chapter lore` | violet | Setting and history |

The chapter's colour says where the reader is: it is every plain panel's tag and rail, the opener's and the footer chip's. What a section is stays its kind's: a reference, lore, dm or catalog sheet keeps its own colour and silhouette in any chapter, so a lore sheet in the Dream Master's chapter still reads as lore.

```markdown
@chapter rules #ch-rules ch="3"

@page chapter-start

# Are You Lucid Yet?
```

Any other word after `@chapter` is the chapter's label, as before. A book adjusts a location with the same selectors and tokens, in its own sheet, and never with a component's background, shadow or pseudo-elements:

```css
.chapter.dc-chapter-rules { --dc-section-accent: var(--blood); }
.page.dc-page-chapter-start .dc-fiction-excerpt { --dc-fiction-art-width: 2.5in; }
```

A panel's edge has tokens of its own, `--dc-section-clip` (the top-right cut, 18px), `--dc-section-cut-tl`, `--dc-section-cut-br` and `--dc-section-cut-bl` (the other three corners, 0) and `--dc-section-rail` (the rail, 5px), so a template changes the silhouette without touching the panel's layers.

The old raw spellings (`@page .page-chapter-start .dc-chapter-start`, `.page-toc`, `.page-credits .dc-credits`, `.page-intro`, `.dc-citizen-file-page`) are no longer styled. Write the word.

## Contents page

`@toc` turns an ordered list into the contents rows; a `[link](#id)` on an item resolves to its page number at build time.

```markdown
@page contents

# Contents

@lede

Twelve chapters of dreams, dirt, and what bites back.

@end-lede

@toc

1. [Who Do You Dream to Be?](#ch-citizen) --- Citizen file, vibe, origins.
2. [What Do You Dream of Doing?](#ch-specialties) --- How abilities work.
3. [The Augmerc](#ch-augmerc) --- Muscle for hire.

@end-toc
```

Rendered: [Front Matter](#ch-example-front-matter).

## Credits page

A chevron title, a lede for thanks and dedications, and the colophon, a `@section flat` with its names in `@columns 2`: bold lead-ins become role labels. The title of the contents, credits and intro pages is a chevron banner because of the page word; write `{.dc-chevron}` only on a heading anywhere else.

```markdown {.dg-split}
@page credits

# Credits

@lede

**Special Thanks:** everyone who broke the rules so we could fix them.

@end-lede

@section flat

@columns 2

**Designers:** TWard and ITLackey

**Artist:** Scott Georges

**Edition & ISBN:** First Edition · ISBN pending.

@end-columns

@end-section
```

Rendered: [Front Matter](#ch-example-front-matter).


## Chapter opener

A chapter opens on `@page chapter-start` with its `# Title` (a banner in the chapter's accent). Its pages carry the folio and chapter chip like any other page, so an opener that runs onto a second page stays numbered. A fiction excerpt can open the chapter: `@fiction-excerpt` sets narrative typography and floats the first image in the flow.

```markdown {.dg-split}
@chapter #ch-citizen ch="1"

@page chapter-start

# Who Do You Dream to Be?

@fiction-excerpt

"It's hard being me, but I guess it's the same for anyting sentient in the monoverse, ay?!"

![Lil Thump](img/placeholder-lil-thump.png)

I wuz tearin down an alley, lungs burnin, heart jackhammering like it wanted out.

@end-fiction-excerpt

@page

@section panel

## Citizen File

Thump is a PC created for dreams in Dimm City by an actual dreamer.

@end-section
```

Rendered: [Chapter Opener](#ch-example-chapter-opener). Tokens for the excerpt: `--dc-fiction-bg`, `--dc-fiction-cavity`, `--dc-fiction-line-height`, `--dc-fiction-art-float`, `--dc-fiction-art-width`.

The snippet picker's *Chapter Start Page* inserts this opener.

## Citizen File walkthrough

`@citizen-walkthrough` is the chassis for a character-creation step: a `####` field name and the prose that walks through it. Put two short fields side by side in `@columns 2` inside it. Pair it with `@page citizen-file` for the running header.

```markdown
@page citizen-file

@citizen-walkthrough

@columns 2

#### What's Yr Handle?

Choose a name. Pull it from a book, a show, a half-remembered dream.

#### Designation

Let others know how to refer to you. She/her, he/him, they/them, or something else entirely.

@end-columns

@end-citizen-walkthrough
```

Result {.dg-result}

<div class="dg-stage">

@citizen-walkthrough

@columns 2

#### What's Yr Handle?

Choose a name. Pull it from a book, a show, a half-remembered dream.

#### Designation

Let others know how to refer to you. She/her, he/him, they/them, or something else entirely.

@end-columns

@end-citizen-walkthrough

</div>


## Specialty catalog page

`@page specialty-catalog` plus a `@card-grid` of specialty cards, each in its own `@specialty`. The word makes the catalog a designed two-page spread: it opens on a left page, so the two pages face each other (the word forces no blank page when the chapter opener before it is on the facing right page, as it is meant to be; an opener that lands on a left page makes the engine insert one, so keep the opener on a right page); the title, four cards and Dualist fill the left page and the other four cards and Generalist the right (list Dualist fifth and Generalist last, and put a short `@lede` right after Dualist to open the right page; Dualist and Generalist span both columns; every one-column card is one size and both full-width cards another), in aligned rows, each card a poster with its portrait on top, its name, its tagline and its pitch. Whatever follows starts the next page: write a plain `@page` after `@end-card-grid`. Keep the cards uniform --- identical chrome is what makes the choices comparable. The same `@card-grid` on no such page (as in the Variant Gallery) is the dense card with a small floated thumbnail.

```markdown {.dg-split}
@page specialty-catalog

## Choose Your Specialty {.dc-chevron}

@lede

Every dreamer's got a sharp edge --- your specialty is where it starts.

@end-lede

@card-grid

@columns 2

@specialty .augmerc

@specialty-card #specialty-augmerc

### Augmerc

![Augmerc](img/specialty-augmerc-card.png)

> Cybernetic Commando

Heavily armed and wired for war.

@end-specialty-card

@end-specialty

@end-columns

@end-card-grid
```

Rendered with all ten cards: [Specialty Overview](#ch-example-specialty-overview).

## Specialty profile

Intro, art plate, then learning paths with their skill cards, all inside one `@specialty`. Write the intro first: it opens a left-hand page and the art plate faces it on the right. Each learning path opens a page of its own. The plate keeps no fill behind its picture, so transparent art stands on the page's brick, or on the specialty's wall when it names one.

```markdown {.dg-split}
@specialty .augmerc

@specialty-intro

## Augmerc

...

@end-specialty-intro

@specialty-art

![Augmerc](img/specialty-augmerc-art.png)

@end-specialty-art

@learning-path

### Biting Distance

> If you can touch it, you can maul it.

- Punishing Counter
- Rage Hit

@skill

#### Punishing Counter

...

@end-skill

@end-learning-path

@end-specialty
```

Rendered: [Specialty Profile](#ch-example-specialty-profile).

## Choice page

Flaws, ideals, and dreams: a `@flaws` (or `@ideals`, `@dreams`) of `@card` blocks. The section class sets each card's colour, silhouette and chip (Flaw: blood, a cracked edge; Ideal: HUD blue, a steady tablet; Dream: violet, a rising edge). Cards stack in one column; use a tape divider between runs rather than columns.

```markdown
@ideals

## 4. Ideal

Your **Ideal** is the belief you fall back on when things get loud.

@card

#### Honor

You believe in a code, and it's your duty to uphold it.

> "I made a promise to help those in need."

@end-card

@end-ideals
```

## Running headers and footers

Body pages print `p.N` (the page number) and `c.N` (the chapter number) in opposing bottom corners, swapping on verso. Front matter, chapter starts, and full-bleed pages print none. `c.N` comes from `@chapter ... ch="N"`: write it at the top of every chapter file and nothing else is needed.
