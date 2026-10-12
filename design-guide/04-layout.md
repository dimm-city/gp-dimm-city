@chapter #ch-layout .layout .dg-guide ch="4"

@page .dg-doc

Chapter 4 {.dg-kicker}

# Layout

How content is arranged inside a page: columns, sidebars, floated art, and the handful of classes that control where things break. Everything here is a marker, a class on `@section`, `@page`, or an image. {.dg-lede}


## Columns

`@columns` is Gutterpress's one way to set content in columns: `@columns 2` to `@columns 5`, closed by `@end-columns`. Text fills the first column and overflows into the next; `@column-break` forces the next column.

```markdown
@columns 2

Left column. Text fills top to bottom and overflows right.

@column-break

Right column.

@end-columns
```

Result {.dg-result}

<div class="dg-stage dg-on-paper">

@columns 2

Left column. Text fills top to bottom and overflows right.

@column-break

Right column.

@end-columns

</div>

`@columns 3` is the same marker with a 3. A run's columns balance, so a short run ends level. Whatever wants columns goes inside `@columns`: paragraphs, a list, a run of entries. The components in this guide take it the same way, for example `@columns 2` inside a `@skill`, a `@card-grid` or an `@npc-stat`.

## A card with columns

A column run inside a `@section panel` sits in the standard card: the leading `##` or `###` is the heading bar at full width, and `@columns 2` below it splits the body.

```markdown
@section panel

## The City

@columns 2

Dimm City twitches like a clamped nerve at the edge of existence.

@column-break

Nothing here is safe. Nothing here is free.

@end-columns

@end-section
```

Result {.dg-result}

<div class="dg-stage">

@section panel

## The City

@columns 2

Dimm City twitches like a clamped nerve at the edge of existence.

@column-break

Nothing here is safe. Nothing here is free.

@end-columns

@end-section

</div>

## Sidebar

`@sidebar` floats a reference panel to the right at 38% width; body text wraps on its left. Give it running prose on both sides so it never strands in white space.

```markdown
When the Dreamers push past Too Far, the table starts asking how movement works.

@sidebar

### Distance, Fast

Three bands, no grid. **In Reach** is one swing away. **Nearby** is a burned Move. **Too Far** might as well be the other side of the ether.

@end-sidebar

Keep the bands fictional, not metric. The Dream Master sets the band; the dice decide whether you close it.
```

Result {.dg-result}

<div class="dg-stage dg-on-paper">

When the Dreamers push past Too Far, the table starts asking how movement works.

@sidebar

### Distance, Fast

Three bands, no grid. **In Reach** is one swing away. **Nearby** is a burned Move. **Too Far** might as well be the other side of the ether.

@end-sidebar

Keep the bands fictional, not metric. The Dream Master sets the band; the dice decide whether you close it. A Dreamer who wants to cross two bands in one turn is telling you they're willing to spend everything to get there — let them, and let it cost.

</div>

@page .dg-doc

## Floated images

An image on its own line is a figure. `.dc-img-float-right` or `.dc-img-float-left` floats it at 44% of the column with text wrapping around it; leave a blank line after the paragraph that should clear it.

```markdown
![Scavenger](img/scavenger.png){.dc-img-float-right}

Blasts lit the dusk like glitchfire. Bolts and teeth and claws tangled mid-air.
```

Result {.dg-result}

<div class="dg-stage dg-on-paper">

![Scavenger](img/scavenger.png){.dc-img-float-right}

Blasts lit the dusk like glitchfire. Bolts and teeth and claws tangled mid-air. Neon signs cracked. Alleyways bled smoke. Debris rained in bursts. This wasn't about glory — it was turf. It was pride. It was blood memory, raw and ugly, of family torn away by their rival.

DimmCitz scattered, vanished into bolted dens and reinforced rooftops. The air stank of scorched fur, ozone, and cordite.

</div>

A `@fiction-excerpt` places its first image for you — see [Page Templates](#ch-templates).

## Break control

Cards and callouts keep themselves whole by default: they move to the next page rather than split. A section does the opposite: it splits where the page ends. Two classes change that, and a third forces a break.

| You write | Effect |
|---|---|
| `@section panel .dc-avoid-split` | Keep this section whole: it moves to the next page rather than splitting |
| `@section .gp-no-break` | Core's own never-split class, for a section of any kind |
| `@skill {.dc-allow-split}` | Allow this one tall skill card to split instead of leaving a page mostly empty |
| `## Heading {.gp-break-before}` | Start a new page before this element |
| `@page-break` | Start a new page here |

Reach for `.dc-avoid-split` on a short section that would read badly in two halves; a section kept whole leaves a dead zone at the foot of the page before it. Reach for `.dc-allow-split` only when a skill card is genuinely taller than the printable area. Prefer splitting content at a logical boundary first — `@continue` for a long skill card.

## Tighter spacing

`.dc-snug` halves the space between paragraphs and list items inside a section or page. Reach for it when a section overflows by a line or two and the last line would otherwise strand on a page of its own. Type size and leading are untouched.

```markdown
@section panel .dc-snug
### Ideal

Paragraph and list-item gaps shrink to 0.04in here.
@end-section

@page .dc-snug
```

## Edge to edge

`.dc-flush` removes a component's side margins so it runs the full column. It is read by tape, stat blocks, sticker chains, and `@outcome flush`.
