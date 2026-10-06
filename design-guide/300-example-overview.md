@chapter #ch-examples .examples .chapter-03 .dg-guide ch="3"

@page .dg-doc

# Field Guide in Action

Real pages from the Dimm City Field Guide rendered through the DC print system. Every spread in Part 2 uses real game content — actual book text, real specialties, verbatim rules — built from the same markdown and CSS as the published book. Artwork is the one deliberate exception: where final art has not yet been commissioned, a `placehold.co` placeholder image stands in at the correct size. This is the project's proofing approach — the layout is final, the images are proxies. {.dg-lede}

## What Part 2 is

Part 1 shows each component on its own. Part 2 is the payoff: whole pages of the Dimm City Field Guide, rendered live from the same markdown and CSS as the published book, so you can see how the components combine under real conditions — how a chapter opens, how a specialty profile flows across pages, how a Dream Master's reference pages read.

Each chapter is the book's own markdown, verbatim. Artwork is the one substitution: where final art has not been commissioned, a `placehold.co` placeholder stands in at the correct size. If something looks wrong on these pages, it is a real bug in the package, not a specimen issue.

## Part 2 contents

<div class="dg-toc">
<ol>
<li><a href="#ch-example-front-matter">Front Matter</a> — contents, credits, and introduction pages</li>
<li><a href="#ch-example-chapter-opener">Chapter Opener</a> — a labelled chapter with a fiction excerpt, then the Citizen File walkthrough</li>
<li><a href="#ch-example-specialty-overview">Specialty Overview</a> — the opener fiction and the ten-card specialty catalog</li>
<li><a href="#ch-example-specialty-profile">Specialty Profile</a> — the Augmerc: intro, art plate, a learning path with skill cards, DM notes</li>
<li><a href="#ch-example-rules">Rules Pages</a> — tabbed sections, column panels, definitions, conditions, the outcome ladder</li>
<li><a href="#ch-example-dm-npcs">DM &amp; NPC Pages</a> — DM notes, tape dividers, narrative NPC stat blocks, a procedure</li>
<li><a href="#ch-example-gear-tech">Gear &amp; Tech</a> — gear and note callouts, an ego-point ladder, gear entries in columns</li>
</ol>
</div>

## What each chapter exercises

| Chapter | Page templates | Components |
|---|---|---|
| Front Matter | `.page-toc`, `.page-credits .dc-credits`, `.page-intro` | `@toc`, `@lede`, `.credits-colophon`, `[!PULLQUOTE]`, floated art |
| Chapter Opener | labelled `@chapter` + `@page intro`, `.dc-citizen-file-page` | `.dc-fiction-excerpt`, `---{.column-break}`, `@callout variant=origin`, `.dc-citizen-walkthrough` |
| Specialty Overview | `@page intro`, `.card-grid` | `.dc-card-grid`, `@specialty` × 10, `@specialty-card`, `@procedure`, `.dc-spray` |
| Specialty Profile | `@page` | `@specialty-intro`, `@specialty-art`, `@learning-path`, `@skill` with tiers and outcome tables, `@dm-note`, `@procedure` |
| Rules Pages | `@page intro` | `.dc-tabbed`, `.dc-column-panel`, `@definition`, `@callout variant=note`, `@outcome`, a conditions table |
| DM & NPC Pages | `@page` | `@dm-note`, `@tape`, `.dc-npc-stat` × 3, `@procedure`, tables |
| Gear & Tech | `@page` | `@callout variant=gear`, `@outcome`, `@gear` in `.dc-column-panel` columns |
