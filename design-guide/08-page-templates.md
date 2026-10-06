@chapter #ch-templates .templates .dg-guide ch="8"

@page

# Page Templates

@lede

Classes on `@page` choose a page's geometry — margins, footers, running headers — and a few `@section` chassis build the recurring pages of a Dimm City book. Each template below is a skeleton to copy; the finished page is in Part 2.

@end-lede


## Page geometry

US Letter, perfect-bound, with bleed. Declared in `manifest.yaml`; the `@page` rules in the package's `styles/page-rules.css` set the rest.

| Dimension | Value |
|---|---|
| Trim | 8.5 × 11 in |
| Bleed | 0.125 in, all sides |
| Top / bottom margin | 0.5 in / 0.70 in (footer sits in the bottom margin) |
| Binding gutter / outside | 0.75 in / 0.5 in, swapping per recto and verso |

Extend any full-bleed image 0.125 in past the trim.

## Page classes

| You write | Footers | Use for |
|---|---|---|
| `@page` | `p.N` and `c.N` in opposing corners | Every body page |
| `@page .page-toc` | none | The contents page |
| `@page .page-credits .dc-credits` | none | The credits page |
| `@page .page-intro` | none | The introduction |
| `@page .page-chapter-start .dc-chapter-start` | none | A chapter opener |
| `@page intro` | `p.N`, `c.N` | A chapter's first page under a labelled `@chapter` — the chapter badge is injected here |
| `@page .page-sidebar` | `p.N`, `c.N` | A page with an inset sidebar rail |
| `@page .dc-citizen-file-page` | `p.N`, `c.N` | Running header "Citizen File" |
| `@page .card-grid` | `p.N`, `c.N` | The specialty catalog page |
| `@page .dc-full-page` | none | Zero margins; full-bleed art |
| `@page .dc-suppress-footer` | none | Any page that should print no footer |

The `c.N` footer is the chapter number from `@chapter … ch="N"`. A chapter split across files repeats its `@chapter` line in each.


## Contents page

`@toc` turns an ordered list into the contents rows; a `[link](#id)` on an item resolves to its page number at build time.

```markdown
@page .page-toc

# Contents {.dc-chevron}

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

A chevron title, a lede for thanks and dedications, and the colophon grid: bold lead-ins become role labels.

```markdown
@page .page-credits .dc-credits

# Credits {.dc-chevron}

@lede

**Special Thanks:** everyone who broke the rules so we could fix them.

@end-lede

@section .credits-colophon

<div class="dc-colophon-grid">

**Designers:** TWard and ITLackey

**Artist:** Scott Georges

**Edition & ISBN:** First Edition · ISBN pending.

</div>

@end-section
```

Rendered: [Front Matter](#ch-example-front-matter).


## Chapter opener

A labelled `@chapter` plus `@page intro` gets the stacked chapter badge on its first page automatically. A fiction excerpt opens the chapter: `@section .dc-fiction-excerpt` sets narrative typography and floats the first image in the flow. `---{.column-break}` splits fiction from the rules column that follows.

```markdown
@chapter C.01 #ch-citizen ch="1"

@page intro

@section .dc-fiction-excerpt

# Who Do You Dream to Be?

"It's hard being me, but I guess it's the same for anyting sentient in the monoverse, ay?!"

![Lil Thump](https://placehold.co/600x400/png?text=Lil+Thump)

I wuz tearin down an alley, lungs burnin, heart jackhammering like it wanted out.

@end-section

---{.column-break}

@section

## Citizen File

Thump is a PC created for dreams in Dimm City by an actual dreamer.

@end-section
```

Rendered: [Chapter Opener](#ch-example-chapter-opener). Tokens for the badge: `--dc-chapter-opener-bg`, `--dc-chapter-opener-accent`; for the excerpt: `--dc-fiction-bg`, `--dc-fiction-art-float`, `--dc-fiction-art-width`.

The footer-free variant is `@page .page-chapter-start .dc-chapter-start` with a `# Title` — the snippet picker's *Chapter Start Page*.

## Citizen File walkthrough

`@section .dc-citizen-walkthrough` is the chassis for a character-creation step: a `####` field name and the prose that walks through it. Add `.gp-columns-2 .dc-column-panel` to put two short fields side by side. Pair it with `@page .dc-citizen-file-page` for the running header.

```markdown
@page .dc-citizen-file-page

@section .dc-citizen-walkthrough .gp-columns-2 .dc-column-panel

#### What's Yr Handle?

Choose a name. Pull it from a book, a show, a half-remembered dream.

#### Designation

Let others know how to refer to you. She/her, he/him, they/them, or something else entirely.

@end-section
```

Result {.dg-result}

@section .dc-citizen-walkthrough .gp-columns-2 .dc-column-panel

#### What's Yr Handle?

Choose a name. Pull it from a book, a show, a half-remembered dream.

#### Designation

Let others know how to refer to you. She/her, he/him, they/them, or something else entirely.

@end-section


## Specialty catalog page

`@page .card-grid` plus a `@section .dc-card-grid` of specialty cards, each in its own `@specialty`. Keep the cards uniform — identical chrome is what makes the choices comparable.

```markdown
@page .card-grid

## Choose Your Specialty {.dc-chevron}

@lede

Every dreamer's got a sharp edge — your specialty is where it starts.

@end-lede

@section .dc-card-grid

@specialty .augmerc

@specialty-card #specialty-augmerc

### Augmerc

![Augmerc](https://placehold.co/300x340/png?text=Augmerc)

> Cybernetic Commando

Heavily armed and wired for war.

@end-specialty-card

@end-specialty

@end-section
```

Rendered with all ten cards: [Specialty Overview](#ch-example-specialty-overview).

## Specialty profile

Intro, art plate, then learning paths with their skill cards, all inside one `@specialty`. The art plate takes its own page.

```markdown

@specialty .augmerc

@specialty-intro

## Augmerc

…

@end-specialty-intro

@specialty-art

![Augmerc](https://placehold.co/600x800/png?text=AUGMERC)

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

Flaws, ideals, and dreams: a `@section .dc-flaws` (or `.dc-ideals`, `.dc-dreams`) of `@card` blocks. The section class colors every card's accent. Cards stack in one column; use a tape divider between runs rather than columns.

```markdown

@section .dc-ideals

## 4. Ideal

Your **Ideal** is the belief you fall back on when things get loud.

@card

### Honor

You believe in a code, and it's your duty to uphold it.

> "I made a promise to help those in need."

@end-card

@end-section
```

## Running headers and footers

Body pages print `p.N` (the page number) and `c.N` (the chapter number) in opposing bottom corners, swapping on verso. Front matter, chapter starts, and full-bleed pages print none. `c.N` comes from `@chapter … ch="N"`: write it at the top of every chapter file and nothing else is needed.
