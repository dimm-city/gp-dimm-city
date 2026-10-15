@chapter #ch-templates .templates .dg-guide ch="8"

@page .dg-doc

Chapter 8 {.dg-kicker}

# Page Templates

A word on `@page` chooses a page's geometry — margins, footers, running headers — and `@section` variants build the recurring pages of a Dimm City book. Each template below is a skeleton to copy; the finished page is in Part 2. {.dg-lede}


## Page geometry

US Letter, perfect-bound, with bleed: the gutterpress `dtrpg` preset, declared in `manifest.yaml`. The geometry follows DriveThruRPG's published print specification ([Quick Specifications for Print Books](https://help.drivethrupartners.com/hc/en-us/articles/12780800178583-Quick-Specifications-for-Print-Books)): a 0.125 in bleed on the three outside edges and none on the binding edge; all text at least 0.5 in inside the trim; art that does not bleed at least 0.25 in from the outside edges and 0.5 in from the binding edge.

The `@page` rules in the package's `styles/page-rules.css` set the margins on the sheet, which includes the bleed, so each bleed-side margin is the trim distance plus 0.125 in.

| Dimension | On the sheet | From the trim | DriveThruRPG minimum for text |
|---|---|---|---|
| Sheet (trim + bleed) | 8.625 × 11.25 in | — | — |
| Trim | — | 8.5 × 11 in | — |
| Bleed | 0.125 in at top, bottom and the outside edge; none at the spine | — | — |
| Top margin | 0.625 in | 0.5 in | 0.5 in |
| Bottom margin (the folio and chapter chips sit in it) | 0.875 in | 0.75 in | 0.5 in — the chips are centred in the band and print about 0.2 in from the trim |
| Outside margin | 0.625 in | 0.5 in | 0.5 in |
| Binding margin | 0.75 in | 0.75 in | 0.5 in |

A page carrying the "Citizen File" running head has a 0.875 in top margin, so the head itself sits 0.5 in inside the trim. Margins swap per recto and verso: the binding margin is on the spine side. Extend any full-bleed image 0.125 in past the trim.

## Page words

| You write | Footers | Use for |
|---|---|---|
| `@page` | `p.N` and `c.N` in opposing corners, the chapter's name between | Every body page |
| `@page contents` | none | The contents page |
| `@page credits` | none | The credits page |
| `@page intro` | none | The introduction (a `@lede`, then a `@section flat`) |
| `@page chapter-start` | none | A chapter opener |
| `@page citizen-file` | `p.N`, `c.N` | Running header "Citizen File" |
| `@page specialty-catalog` | `p.N`, `c.N` | The specialty catalog: a two-page spread that opens on a left page |
| `@page full-bleed` | none | Zero margins; full-bleed art (core's word; the raw `.dc-full-page` is styled the same) |
| `@page blank` | none | A deliberately blank page (core's word) |

The `c.N` footer is the chapter number from `@chapter … ch="N"`. A chapter split across files repeats its `@chapter` line in each.

### The page chips

The folio and the chapter number print as stickers, never as bare type. The folio (`P.121`) is a paper-cream sticker with an ink edge and a hard shadow; the chapter chip (`C.N`, which a book can restate as `E.N` as this guide does for Part 2) is a stamped coupon: a solid face with cream type and the same edge and shadow. Both are 17 pt tall with 10 pt type centred in the face, and both sit 0.125 in below the text block, inside DriveThruRPG's 0.5 in text minimum, so a box that runs to the foot never touches them, on recto and verso, for every page word that prints them. The coupon is magenta by default; to colour it with a chapter, put the chapter's pages on a named page, `:where(#ch-rules) > .page { page: dc-chip-rust; }` (blue, rust, violet, amethyst or amber; the `specialty`, `rules` and `lore` chapter words do it for you). Name the page with the low-specificity `:where()` so a page's own template name still wins. A `citizen-file` page's running head is the same sticker in amber at the top.

### Where pages break

Pagination is part of the package, so every book gets it: a panel of four blocks or fewer stays whole and moves to the next page rather than splitting 3 + 1; a longer panel never opens or ends with one block alone; text keeps three orphans and three widows in panels and callouts; a skill card splits between ability rows, never leaving one row on a page with a hand's breadth of empty cream under it; headings, tape dividers and stat-block names stay with what follows. A box that must be kept whole whatever it costs is `{.dc-avoid-split}`; a book's own `--dc-section-break-inside: auto` lets one split.

### Text on the wall

Nothing is ever printed straight on the brick. Anything you write directly on a page with no `@section` or callout around it dresses itself:

| You write | It prints as |
|---|---|
| `# Title` | A banner in the chapter's accent colour with cream type |
| `## Heading` | A paper slip: an accent rail on the left, a dashed ink foot, a hard shadow and a strip of masking tape |
| `### Heading` | A tag that shrinks to its words, hung in from the left (every second one hangs further), no tape |
| `#### Heading` and smaller | A label slip that shrinks to its words |
| Paragraphs, lists, quotes | One paper sheet per run; the sheet ends where the run does |

Headings that already carry a look (`{.dc-chevron}`, `{.dc-spray}`) and everything inside a section keep their own. The chapter word recolours the rail and the banner. To change the slip or sheet for a book, set `--dc-page-slip-bg`, `--dc-page-slip-ink`, `--dc-page-slip-edge`, `--dc-page-slip-shadow`, `--dc-page-slip-tape`, `--dc-page-slip-gap` (the space above a slip), `--dc-page-slip-offset`, `--dc-page-sheet-pad` or `--dc-page-title-ink`. A plain heading that follows a box (a ladder, a stat grid, a table) takes `--dc-heading-gap` above it. Explainer pages like the one you are reading (`@page .dg-doc`) print plain on white and are not wall pages.


## Where the content sits

A location is the page template or the chapter a section sits in. It draws nothing: it sets tokens, and the components read them. That is how one `@section panel` looks right in an opener, in a rules chapter and in a lore chapter without a rule per book.

A **chapter word** sets the colour register of every panel in the chapter. It recolours a panel's accent and nothing else: an alert, a faction, a choice card or a gear entry keeps its own identity in every chapter, so a warning is a hazard sign and a Dream Master note is an ink slab wherever they sit:

| You write | Section accent | Use for |
|---|---|---|
| `@chapter citizen-file` | magenta-deep | Who you dream to be |
| `@chapter specialty` | blue-dark | The specialty gateway |
| `@chapter rules` | rust | Rules chapters |
| `@chapter lore` | violet | Setting and history |

```markdown
@chapter rules #ch-rules ch="3"

@page chapter-start

# Are You Lucid Yet?
```

Any other word after `@chapter` is the chapter's label, as before. A book adjusts a location with the same selectors and tokens, in its own sheet, and never with a component's background, shadow or pseudo-elements:

```css
.chapter.dc-chapter-rules { --dc-section-accent: var(--blood); }
.page.dc-page-chapter-start .dc-fiction-excerpt { --dc-fiction-depth: 12px; }
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

1. [Who Do You Dream to Be?](#ch-citizen) — Citizen file, vibe, origins.
2. [What Do You Dream of Doing?](#ch-specialties) — How abilities work.
3. [The Augmerc](#ch-augmerc) — Muscle for hire.

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

A chapter opens on `@page chapter-start` with its `# Title` (a banner in the chapter's accent) and no footer. A fiction excerpt can open the chapter: `@fiction-excerpt` sets narrative typography and floats the first image in the flow.

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

Rendered: [Chapter Opener](#ch-example-chapter-opener). Tokens for the excerpt: `--dc-fiction-bg`, `--dc-fiction-depth`, `--dc-fiction-depth-bg`, `--dc-fiction-cavity`, `--dc-fiction-art-float`, `--dc-fiction-art-width`. On a chapter-start page the hole is deeper (a 10px cast shadow) by itself; nothing to add.

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

`@page specialty-catalog` plus a `@card-grid` of specialty cards, each in its own `@specialty`. The word makes the catalog a designed two-page spread: it opens on a left page, so the two pages face each other (the word forces no blank page when the chapter opener before it is on the facing right page, as it is meant to be; an opener that lands on a left page makes the engine insert one, so keep the opener on a right page); the title, the lede and the first four cards fill the left page and the other six the right, in aligned rows of equal height, each card a poster with its portrait on top, its name, its tagline and its pitch, and an index chip (01 to 10) on the portrait. Whatever follows starts the next page: write a plain `@page` after `@end-card-grid`. Keep the cards uniform — identical chrome is what makes the choices comparable. The same `@card-grid` on no such page (as in the Variant Gallery) is the dense card with a small floated thumbnail.

```markdown {.dg-split}
@page specialty-catalog

## Choose Your Specialty {.dc-chevron}

@lede

Every dreamer's got a sharp edge — your specialty is where it starts.

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

Intro, art plate, then learning paths with their skill cards, all inside one `@specialty`. The art plate takes its own page.

```markdown {.dg-split}
@specialty .augmerc

@specialty-intro

## Augmerc

…

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

…

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

Body pages print `p.N` (the page number) and `c.N` (the chapter number) in opposing bottom corners, swapping on verso. Front matter, chapter starts, and full-bleed pages print none. `c.N` comes from `@chapter … ch="N"`: write it at the top of every chapter file and nothing else is needed.
