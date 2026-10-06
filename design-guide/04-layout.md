@chapter #ch-layout .layout .dg-guide ch="4"

@page .dg-doc

# Layout

How content is arranged inside a page: columns, the column panel, sidebars, floated art, and the handful of classes that control where things break. Everything here is a class on `@section`, `@page`, or an image. {.dg-lede}


## Two and three columns

`.gp-columns-2` and `.gp-columns-3` are Gutterpress's own column vocabulary. Text fills the first column and overflows into the next; `@column-break` forces the next column.

```markdown
@section .gp-columns-2

Left column. Text fills top to bottom and overflows right.

@column-break

Right column.

@end-section
```

Result {.dg-result}

<div class="dg-stage">

@section .gp-columns-2

Left column. Text fills top to bottom and overflows right.

@column-break

Right column.

@end-section

</div>

## The column panel

Add `.dc-column-panel` and the run sits in a card: substrate, top and bottom rules, and the leading `##` or `###` becomes a full-width bar spanning both columns, with its first paragraph as a shared preamble. This is the workhorse layout for rules pages.

```markdown
@section .gp-columns-2 .dc-column-panel

## The City

Dimm City twitches like a clamped nerve at the edge of existence.

@column-break

Nothing here is safe. Nothing here is free.

@end-section
```

Result {.dg-result}

<div class="dg-stage">

@section .gp-columns-2 .dc-column-panel

## The City

Dimm City twitches like a clamped nerve at the edge of existence.

@column-break

Nothing here is safe. Nothing here is free.

@end-section

</div>

## Tabbed section

`.dc-tabbed` hangs the section's heading as a tab off the panel edge — a strong break between consecutive topics on one page.

```markdown
@section .dc-tabbed

## Dreamers

You're a Dreamer, not because you're special, but because you're reckless enough to try.

@end-section
```

Result {.dg-result}

<div class="dg-stage">

@section .dc-tabbed

## Dreamers

You're a Dreamer, not because you're special, but because you're reckless enough to try.

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

<div class="dg-stage">

When the Dreamers push past Too Far, the table starts asking how movement works.

@sidebar

### Distance, Fast

Three bands, no grid. **In Reach** is one swing away. **Nearby** is a burned Move. **Too Far** might as well be the other side of the ether.

@end-sidebar

Keep the bands fictional, not metric. The Dream Master sets the band; the dice decide whether you close it. A Dreamer who wants to cross two bands in one turn is telling you they're willing to spend everything to get there — let them, and let it cost.

</div>

### Inset sidebar

`@sidebar .inset` is a full-height rail pinned to the page's edge. It needs the `@page .page-sidebar` template, which reserves the column the rail stands in; on an ordinary page it falls back to the floated sidebar.

```markdown
@page .page-sidebar

Body text for this page stops at the rail's edge.

@sidebar .inset

### Free, Not Costless

One out-of-turn ability per round is free to trigger — but it still spends its listed AP.

@end-sidebar
```

@page .page-sidebar

Result {.dg-result}

Initiative in Dimm City is fast and loose: roll Lucidity, act in order, and remember that out-of-turn abilities still cost AP even when the first use each round is free.

@sidebar .inset

### Free, Not Costless

One out-of-turn ability per round is *free to trigger* — but it still spends its listed AP. Each additional out-of-turn use that round costs **+1 AP** on top.

@end-sidebar

That distinction trips up new tables constantly, so it belongs in the margin right where the rule first bites.

@page .dg-doc

## Floated images

An image on its own line is a figure. `.dc-img-float-right` or `.dc-img-float-left` floats it at 44% of the column with text wrapping around it; leave a blank line after the paragraph that should clear it.

```markdown
![Scavenger](img/scavenger.png){.dc-img-float-right}

Blasts lit the dusk like glitchfire. Bolts and teeth and claws tangled mid-air.
```

Result {.dg-result}

<div class="dg-stage">

![Scavenger](img/scavenger.png){.dc-img-float-right}

Blasts lit the dusk like glitchfire. Bolts and teeth and claws tangled mid-air. Neon signs cracked. Alleyways bled smoke. Debris rained in bursts. This wasn't about glory — it was turf. It was pride. It was blood memory, raw and ugly, of family torn away by their rival.

DimmCitz scattered, vanished into bolted dens and reinforced rooftops. The air stank of scorched fur, ozone, and cordite.

</div>

A `@section .dc-fiction-excerpt` places its first image for you — see [Page Templates](#ch-templates).

## Break control

Components keep themselves whole by default: a card, a callout, a section will move to the next page rather than split. Two classes adjust that, and a third forces a break.

| You write | Effect |
|---|---|
| `@section .gp-no-break` | Never split this section across pages |
| `@skill {.dc-allow-split}` or `@section .dc-allow-split` | Allow this one tall element to split instead of leaving a page mostly empty |
| `## Heading {.gp-break-before}` | Start a new page before this element |
| `@page-break` | Start a new page here |

Reach for `.dc-allow-split` only when an element is genuinely taller than the printable area or keeping it whole leaves most of a page blank. Prefer splitting content at a logical boundary first — `@continue` for a long skill card.

## Edge to edge

`.dc-flush` removes a component's side margins so it runs the full column. It is read by tape, stat blocks, sticker chains, and `@outcome flush`.
