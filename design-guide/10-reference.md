@chapter #ch-reference .reference .dg-guide ch="10"

@page .dg-doc

Chapter 10 {.dg-kicker}

# Reference

Every marker on one page, the options they take, the classes you can add, and the token each component exposes. The chapters before this one show each in use. {.dg-lede}


## Structure (Gutterpress core)

| Marker | Closes | Notes |
|---|---|---|
| `@chapter #id ch="N" [C.NN]` | next `@chapter` / EOF | `ch` prints the footer; a label such as `C.01` adds the chapter badge to the first `@page intro` |
| `@page [.class…]` | next `@page` | Page classes: [Page Templates](#ch-templates) |
| `@spread` | next `@spread` / `@page` | Two facing pages |
| `@section [.class…]` | `@end-section` | A region; bare = styled panel, `.dc-plain` = no chrome |
| `@page-break` · `@column-break` | — | Forced breaks |

## Components (this package)

| Marker | Closes | Options |
|---|---|---|
| `@lede` | `@end-lede` | — |
| `> [!TYPE]` | end of blockquote | `NOTE` `WARNING` `DM` `VIBE` `ORIGIN` `VISIT` `GEAR` `FLAVOR` `PULLQUOTE` |
| `@callout` | `@end-callout` | `variant=` as above (not flavor/pullquote), `label="…"` |
| `@dm-note` | `@end-dm-note` | `label="…"` |
| `@tape` | — | `label="…"` |
| `@block` | `@end-block` | `.dc-panel` `.dc-slate` `.dc-shard` `.dc-codex`, `label="…"` |
| `@sidebar` | `@end-sidebar` | `.inset` (needs `@page .page-sidebar`) |
| `@sidebar-box` | `@end-sidebar-box` | `####` heading, `---`, body |
| `@definition` | `@end-definition` | — |
| `@glossary` | `@end-glossary` | `**term** — gloss` paragraphs |
| `@procedure` | `@end-procedure` | an ordered list |
| `@outcome` | `@end-outcome` | `flush`; rows `roll \| name \| text` |
| `@card` | `@end-card` | inside `@flaws` / `@ideals` / `@dreams` |
| `@column-panel` | `@end-column-panel` | usually with `.gp-columns-2`; a card-less run is a bare `@section .gp-columns-2` |
| `@tabbed` | `@end-tabbed` | first heading (`##` or `###`) hangs as the tab |
| `@card-grid` | `@end-card-grid` | a run of `@specialty` / `@specialty-card` |
| `@citizen-walkthrough` | `@end-citizen-walkthrough` | `####` field names and prose |
| `@fiction-excerpt` | `@end-fiction-excerpt` | prose; the first image floats |
| `@npc-stat` | `@end-npc-stat` | `####` name, `>` flavor, stat lines, `#####` labels |
| `@flaws` · `@ideals` · `@dreams` | `@end-flaws` · `@end-ideals` · `@end-dreams` | a run of `@card` blocks |
| `@gear` | `@end-gear` | `###` name, `*tags*`, body |
| `@toc` | `@end-toc` | an ordered list of `[title](#id) — blurb` |
| `@specialty` | `@end-specialty` / next `@specialty` / `@page` / `@section` / `@chapter` | `augmerc` … `generalist`, as a word or a `.class` |
| `@specialty-intro` | `@end-specialty-intro` | `##` name, `###` spec tweak |
| `@specialty-art` | `@end-specialty-art` | one image |
| `@specialty-card` | `@end-specialty-card` | `#id`; `###` name, image, `>` tagline, pitch |
| `@learning-path` | `@end-learning-path` / next `@learning-path` / end of its specialty | `###` title, `>` subtitle, `- skills`, `**Augment:**` |
| `@skill` | `@end-skill` / next `@skill` / end of its path | `id="…"`, `{.dc-allow-split}` `{.dc-two-col}` `{.dc-highlight}`; `#### Name \| Tier [\| highlight]` |
| `@continue` | — | inside a skill: continuation card |

`@roll-table` and `@options-table` are retired; they parse as nothing. Use a pipe table.


## Classes you can add

| Class | Goes on | Effect |
|---|---|---|
| `.gp-columns-2` · `.gp-columns-3` | `@section` | Two or three columns |
| `.dc-column-panel` | `@section` with columns (or write `@column-panel`) | Card substrate, spanning heading bar |
| `.dc-tabbed` | `@section` | Heading hung as a tab |
| `.dc-plain` | `@section` | No panel chrome |
| `.gp-no-break` | `@section` | Never split across pages |
| `.dc-allow-split` | `@section`, `@skill` | Allow a tall element to split |
| `.gp-break-before` | a heading | New page before it |
| `.dc-npc-stat` | `@section` | Narrative NPC stat block |
| `.dc-fiction-excerpt` | `@section` | Narrative typography, auto art float |
| `.dc-citizen-walkthrough` | `@section` | Citizen File field chassis |
| `.dc-card-grid` | `@section` | Two-across grid of specialty cards |
| `.dc-flaws` · `.dc-ideals` · `.dc-dreams` | `@section` of `@card` | Card accent per step |
| `.credits-colophon` | `@section` on the credits page | Colophon chrome |
| `.dc-chevron` | `#` heading | Chevron banner |
| `.dc-spray` | `##` heading | Spray banner |
| `.dc-spec-tweak` · `.dc-no-top` | `###` heading | Spec-tweak rule; no top margin |
| `.dc-img-float-left` · `.dc-img-float-right` | an image | Float at 44% width |
| `.dc-flush` | tape, stat block, stickers | Edge to edge |

## Inline HTML

| You write | Renders |
|---|---|
| `<span class="dc-tag">Melee</span>` | keyword pill |
| `<span class="dc-classtag augmerc">Augmerc</span>` | specialty identity pill |
| `<span class="dc-ap">2 AP</span>` · `.free` · `.var` | AP chip in prose |
| `<div class="dc-tape dc-flush">Label</div>` | tape, edge to edge |
| `<div class="dc-stat [dc-flush]">…</div>` | four-cell stat grid ([Panels, Cards & Data](#ch-panels)) |
| `<div class="dc-at-a-glance-cards">…</div>` | label/value cards |
| `<div class="dc-sidebar"><div class="dc-human-callout">…` | floated NPC capsule |


## Tokens by component

Reset any of these in a book's own sheet, at `:root` or at a chapter id. Defaults live in the package's `styles/dc-component-defaults.css`; shapes are `polygon(…)` clip-paths.

| Component | Tokens |
|---|---|
| Section chassis | `--dc-section-bg` `--dc-section-accent` `--dc-section-tab-indent` `--dc-section-tab-overlap` |
| Lede | `--dc-intro-bg` `--dc-intro-accent` |
| Flavor | `--dc-flavor-accent` `--dc-flavor-accent-width` `--dc-flavor-color` |
| Pull quote | `--dc-pullquote-accent` `--dc-pullquote-accent-soft` `--dc-pullquote-bg` |
| Alerts, callout, DM note | `--dc-alert-bg` `--dc-alert-border` `--dc-alert-fg` `--dc-alert-label-color` `--dc-alert-border-width` `--dc-alert-label-size` `--dc-alert-body-size` |
| Tape | `--dc-tape-bg` `--dc-tape-border` `--dc-tape-color` |
| Chevron · Spray | `--dc-chevron-bg` `--dc-chevron-color` `--dc-chevron-font-size` · `--dc-spray-bg` `--dc-spray-color` |
| Class tag | `--dc-classtag-color` |
| Roll the die | `--dc-roll-the-die-color` `--dc-roll-the-die-border` |
| Block | `--dc-block-bg` `--dc-block-fg` `--dc-block-accent` `--dc-block-title-bg` `--dc-block-title-fg` |
| Sidebar | `--dc-sidebar-surface` `--dc-sidebar-border` `--dc-sidebar-accent` `--dc-sidebar-inset-column` `--dc-sidebar-inset-gutter` |
| Sidebar box | `--dc-sidebar-box-surface` `--dc-sidebar-box-border` `--dc-sidebar-box-accent` `--dc-sidebar-box-rail` |
| Definition | `--dc-definition-block-surface` `--dc-definition-block-accent` `--dc-definition-block-accent-width` |
| Outcome ladder | `--dc-outcomes-surface` `--dc-outcomes-border` `--dc-outcomes-inner-border` `--dc-outcomes-label-bg` `--dc-outcomes-label-color` `--dc-outcome-key-color` `--dc-outcome-name-color` `--dc-outcome-name-opacity` |
| NPC stat block | `--dc-npc-stat-primary` `--dc-npc-stat-secondary` `--dc-npc-stat-label-color` `--dc-npc-stat-rule` `--dc-npc-stat-rule-width` |
| Fiction excerpt | `--dc-fiction-bg` `--dc-fiction-line-height` `--dc-fiction-art-float` `--dc-fiction-art-width` `--dc-fiction-art-outline` `--dc-fiction-art-shadow` |
| Chapter badge | `--dc-chapter-opener-bg` `--dc-chapter-opener-accent` `--dc-chapter-opener-shadow` `--dc-chapter-opener-clip-tail` `--dc-chapter-opener-pad-top` `--dc-chapter-opener-pad-side` |
| Specialty wrapper | `--spec-accent` `--spec-mid` `--spec-dark` `--dc-skill-tab-shape` `--dc-skill-body-shape` `--dc-path-title-shape` `--dc-path-shell-clip` `--dc-specialty-card-shell-shape` `--dc-specialty-intro-title-shape` `--dc-specialty-intro-clip` |
| Specialty intro | `--dc-specialty-intro-bg` `--dc-specialty-intro-title-bg` `--dc-specialty-intro-title-color` |
| Specialty card | `--dc-specialty-card-bg` `--dc-specialty-card-border` `--dc-specialty-card-accent` `--dc-specialty-card-fg` `--dc-specialty-card-media-height` `--dc-specialty-card-media-width` `--dc-specialty-card-title-align` `--dc-specialty-card-band-height` `--dc-specialty-card-shadow` `--dc-specialty-card-title-color` |
| Learning path | `--dc-path-title-bg` `--dc-path-title-color` `--dc-path-accent` `--dc-path-shell-padding-top` `--dc-path-shell-padding-bottom` `--dc-arrow-color` |
| Skill card | `--dc-card-accent` `--dc-card-surface` `--dc-card-tab-bg` `--dc-card-tab-title-color` `--dc-card-body-mark` `--dc-card-gap` `--dc-card-tab-shadow` |
| AP chip | `--dc-ap-bg` `--dc-ap-fg` `--dc-ap-border` |

The brand tokens — `--crimson`, `--orange`, `--rust`, `--amber`, `--blood`, `--hud-blue`, `--hud-magenta`, `--paper-cream`, `--paper-aged`, `--ink`, `--ink-smoke`, `--bg`, and the `--font-*` family — are in [Color](#ch-palette) and [Typography](#ch-typography). The machine-readable catalog of every component, with the DOM it emits and the sheet that owns it, is the package's `components.yaml`.
