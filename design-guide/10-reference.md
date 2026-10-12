@chapter #ch-reference .reference .dg-guide ch="10"

@page .dg-doc

Chapter 10 {.dg-kicker}

# Reference

Every marker on one page, the options they take, the classes you can add, and the token each component exposes. The chapters before this one show each in use. {.dg-lede}


## Structure (Gutterpress core)

| Marker | Closes | Notes |
|---|---|---|
| `@chapter #id ch="N"` | next `@chapter` / EOF | `ch` prints the footer |
| `@page [.class…]` | next `@page` | Page classes: [Page Templates](#ch-templates) |
| `@spread` | next `@spread` / `@page` | Two facing pages |
| `@section [word] [.class…]` | `@end-section` | A region; bare = core's plain box. Words: `panel` `flat` `aside` and the component words (`npc` `fiction` `walkthrough` `cards` `flaws` `ideals` `dreams`) |
| `@columns N` | `@end-columns` | `N` is 1 to 5. The one way to set content in columns; `@column-break` inside it starts the next column |
| `@page-break` · `@column-break` | — | Forced breaks |

## Components (this package)

| Marker | Closes | Options |
|---|---|---|
| `@lede` | `@end-lede` | — |
| `> [!TYPE]` | end of blockquote | `NOTE` `WARNING` `DM` `VIBE` `ORIGIN` `VISIT` `GEAR` `FLAVOR` `PULLQUOTE` |
| `@callout` | `@end-callout` | a variant word: `note` `warning` `dm` `vibe` `origin` `visit` `gear` (`@callout vibe`); `label="…"` |
| `@dm-note` | `@end-dm-note` | `label="…"` (it is `@callout dm`) |
| `@block` | `@end-block` | `.dc-panel` `.dc-slate` `.dc-shard` `.dc-codex`, `label="…"` |
| `@sidebar` | `@end-sidebar` | — |
| `@sidebar-box` | `@end-sidebar-box` | `####` heading, `---`, body |
| `@definition` | `@end-definition` | — |
| `@glossary` | `@end-glossary` | `**term** — gloss` paragraphs |
| `@procedure` | `@end-procedure` | an ordered list |
| `@outcome` | `@end-outcome` | `flush`; rows `roll \| name \| text` |
| `@card` | `@end-card` | inside `@flaws` / `@ideals` / `@dreams` |
| `@card-grid` | `@end-card-grid` | a run of `@specialty` / `@specialty-card` inside `@columns 2` |
| `@citizen-walkthrough` | `@end-citizen-walkthrough` | `####` field names and prose; `@columns 2` inside sets two fields side by side |
| `@fiction-excerpt` | `@end-fiction-excerpt` | prose; the first image floats |
| `@npc-stat` | `@end-npc-stat` | `####` name, `>` flavor, stat lines, `#####` labels; `@columns 2` inside sets the entries in columns |
| `@flaws` · `@ideals` · `@dreams` | `@end-flaws` · `@end-ideals` · `@end-dreams` | a run of `@card` blocks |
| `@gear` | `@end-gear` | `###` name, `*tags*`, body |
| `@toc` | `@end-toc` | an ordered list of `[title](#id) — blurb` |
| `@specialty` | `@end-specialty` / next `@specialty` / `@page` / `@section` / `@chapter` | `augmerc` … `generalist`, as a word or a `.class` |
| `@specialty-intro` | `@end-specialty-intro` | `##` name, `###` spec tweak |
| `@specialty-art` | `@end-specialty-art` | one image |
| `@specialty-card` | `@end-specialty-card` | `#id`; `###` name, image, `>` tagline, pitch |
| `@learning-path` | `@end-learning-path` / next `@learning-path` / end of its specialty | `###` title, `>` subtitle, `- skills`, `**Augment:**` |
| `@skill` | `@end-skill` / next `@skill` / end of its path | `id="…"`, `{.dc-allow-split}` `{.dc-highlight}`; `#### Name \| Tier [\| highlight]`; `@columns 2` around part of the body |
| `@continue` | — | inside a skill: continuation card |


## Classes you can add

| Class | Goes on | Effect |
|---|---|---|
| `.dc-avoid-split` | `@section` | Keep the section whole; it moves to the next page rather than splitting (sections split by default) |
| `.gp-no-break` | `@section` | Core's never-split class |
| `.dc-allow-split` | `@skill` | Allow a tall skill card to split |
| `.gp-break-before` | a heading | New page before it |
| `.dc-section-panel` · `.dc-section-flat` · `.dc-section-aside` | `@section` | What `@section panel`, `flat` and `aside` write |
| `.dc-npc-stat` | `@section` | What `@npc-stat` and `@section npc` write (with `.dc-section-panel`) |
| `.dc-fiction-excerpt` | `@section` | What `@fiction-excerpt` and `@section fiction` write: aged paper, narrative typography, auto art float |
| `.dc-citizen-walkthrough` | `@section` | What `@citizen-walkthrough` writes (with `.dc-section-panel`) |
| `.dc-card-grid` | `@section` | Density for a run of specialty cards (set in `@columns 2`); no chrome |
| `.dc-flaws` · `.dc-ideals` · `.dc-dreams` | `@section` of `@card` | Card accent per step (with `.dc-section-panel`) |
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
| `<div class="dc-at-a-glance-card">…</div>` in `@columns 3` | label/value cards |
| `<div class="dc-sidebar"><div class="dc-human-callout">…` | floated NPC capsule |


## Tokens by component

Reset any of these in a book's own sheet, at `:root` or at a chapter id. Defaults live in the package's `styles/dc-component-defaults.css`; shapes are `polygon(…)` clip-paths.

| Component | Tokens |
|---|---|
| Section chassis | `--dc-section-bg` `--dc-section-accent` |
| Lede | `--dc-intro-bg` `--dc-intro-accent` |
| Flavor | `--dc-flavor-accent` `--dc-flavor-accent-width` `--dc-flavor-color` |
| Pull quote | `--dc-pullquote-accent` `--dc-pullquote-accent-soft` `--dc-pullquote-bg` |
| Alerts, callout, DM note | `--dc-alert-bg` `--dc-alert-border` `--dc-alert-fg` `--dc-alert-label-color` `--dc-alert-border-width` `--dc-alert-label-size` `--dc-alert-body-size` |
| Tape | `--dc-tape-bg` `--dc-tape-border` `--dc-tape-color` |
| Chevron · Spray | `--dc-chevron-bg` `--dc-chevron-color` `--dc-chevron-font-size` · `--dc-spray-bg` `--dc-spray-color` |
| Class tag | `--dc-classtag-color` |
| Roll the die | `--dc-roll-the-die-color` `--dc-roll-the-die-border` |
| Block | `--dc-block-bg` `--dc-block-fg` `--dc-block-accent` `--dc-block-title-bg` `--dc-block-title-fg` |
| Sidebar | `--dc-sidebar-surface` `--dc-sidebar-border` |
| Sidebar box | `--dc-sidebar-box-surface` `--dc-sidebar-box-border` `--dc-sidebar-box-accent` `--dc-sidebar-box-rail` |
| Definition | `--dc-definition-block-surface` `--dc-definition-block-accent` `--dc-definition-block-accent-width` |
| Outcome ladder | `--dc-outcomes-surface` `--dc-outcomes-border` `--dc-outcomes-inner-border` `--dc-outcomes-label-bg` `--dc-outcomes-label-color` `--dc-outcome-key-color` `--dc-outcome-name-color` `--dc-outcome-name-opacity` |
| NPC stat block | `--dc-npc-stat-primary` `--dc-npc-stat-secondary` `--dc-npc-stat-label-color` `--dc-npc-stat-rule` `--dc-npc-stat-rule-width` |
| Fiction excerpt | `--dc-fiction-bg` `--dc-fiction-line-height` `--dc-fiction-art-float` `--dc-fiction-art-width` `--dc-fiction-art-outline` `--dc-fiction-art-shadow` |
| Specialty wrapper | `--spec-accent` `--spec-mid` `--spec-dark` `--dc-skill-tab-shape` `--dc-skill-body-shape` `--dc-path-title-shape` `--dc-path-shell-clip` `--dc-specialty-card-shell-shape` `--dc-specialty-intro-title-shape` `--dc-specialty-intro-clip` |
| Specialty intro | `--dc-specialty-intro-bg` `--dc-specialty-intro-title-bg` `--dc-specialty-intro-title-color` |
| Specialty card | `--dc-specialty-card-bg` `--dc-specialty-card-border` `--dc-specialty-card-accent` `--dc-specialty-card-fg` `--dc-specialty-card-media-height` `--dc-specialty-card-media-width` `--dc-specialty-card-title-align` `--dc-specialty-card-band-height` `--dc-specialty-card-shadow` `--dc-specialty-card-title-color` |
| Learning path | `--dc-path-title-bg` `--dc-path-title-color` `--dc-path-accent` `--dc-path-shell-padding-top` `--dc-path-shell-padding-bottom` `--dc-arrow-color` |
| Skill card | `--dc-card-accent` `--dc-card-surface` `--dc-card-tab-bg` `--dc-card-tab-title-color` `--dc-card-body-mark` `--dc-card-gap` `--dc-card-tab-shadow` |
| AP chip | `--dc-ap-bg` `--dc-ap-fg` `--dc-ap-border` |

The brand tokens — `--crimson`, `--orange`, `--rust`, `--amber`, `--blood`, `--hud-blue`, `--hud-magenta`, `--paper-cream`, `--paper-aged`, `--ink`, `--ink-smoke`, `--bg`, and the `--font-*` family — are in [Color](#ch-palette) and [Typography](#ch-typography). The machine-readable catalog of every component, with the DOM it emits and the sheet that owns it, is the package's `components.yaml`.
